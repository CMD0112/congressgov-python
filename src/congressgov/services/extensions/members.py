"""
Query and convenience methods for the Members model.

Registered dynamically via ``_registry`` so Members stay plain data models.

Field Mappings:
- state: Supports both codes ("CA") and full names ("California")
  Uses StateCode enum for automatic expansion

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_state(), by_party(), by_chamber(), etc.
- Utility methods: current(), democrats(), republicans()
- List as plain list: query().to_list()
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__ (collections_registry)
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ._registry import register_method
from ._query_builder import create_query_builder, FieldMapping

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.member import Members, Member

# Import the actual class for registration
from congressgov.models.entities.member import Members
import congressgov.models.entities.member as member_module

# Import enum for state code mapping
from congressgov.models.base.enums import StateCode


# Import Member class for validation
from congressgov.models.entities.member import Member

MembersQuery = create_query_builder(
    collection_class=Members,
    items_field="members",
    item_class=Member,
    field_mappings={
        "state": FieldMapping(enum_class=StateCode),
        # Example: "partyName": FieldMapping(enum_class=PartyCode)
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
member_module.MembersQuery = MembersQuery

if not TYPE_CHECKING:
    globals()['MembersQuery'] = MembersQuery


@register_method(Members)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        # Start a query chain (lazy by default on query builder)
        members.query().filter(state="CA", lazy=True).order_by("lastName").execute()
    """
    return MembersQuery(self.members or [])


@register_method(Members)
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Members)
def by_state(self, state: str) -> Members:
    """Get members from a specific state (always eager, returns Members)."""
    return self.query().filter(state=state)


@register_method(Members)
def by_party(self, party: str) -> Members:
    """Get members of a specific party (always eager, returns Members)."""
    return self.query().filter(partyName=party)


@register_method(Members)
def by_chamber(self, chamber: str) -> Members:
    """
    Get members by chamber ("House of Representatives" or "Senate").
    Checks the latest term (always eager, returns Members).
    """
    def is_in_chamber(m: Member) -> bool:
        if not m.terms or not m.terms.item:
            return False
        items = m.terms.item if isinstance(m.terms.item, list) else [m.terms.item]
        if not items:
            return False
        latest = max(items, key=lambda t: getattr(t, "startYear", 0) or 0)
        return getattr(latest, "chamber", None) == chamber
    
    return self.query().where(is_in_chamber)


@register_method(Members)
def current(self) -> Members:
    """Get only current members (always eager, returns Members)."""
    return self.query().filter(currentMember=True)


@register_method(Members)
def democrats(self) -> Members:
    """Get all Democratic members (always eager, returns Members)."""
    return self.by_party("Democratic")


@register_method(Members)
def republicans(self) -> Members:
    """Get all Republican members (always eager, returns Members)."""
    return self.by_party("Republican")


@register_method(Members)
def group_by(self, field: str):
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)


# The remaining methods operate on individual Member instances, fetching
# related data (sponsorship, cosponsorship) from the API on demand.
from typing import Any, Optional
from congressgov._client.api.member import (
    member_sponsorship_list_sync,
    member_cosponsorship_list_sync,
)
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.config import MAX_PAGINATION_LIMIT
from congressgov.services.core.expansion_helpers import (
    bind_related_attribute,
    expand_sync_instance,
    extract_parameters_from_target,
)


def _coerce_sponsorship_limit(limit: int | str | None) -> int | None:
    """Map ``limit='max'`` to the API maximum page size (250)."""
    if limit is None:
        return None
    if isinstance(limit, str) and limit.lower() == "max":
        return MAX_PAGINATION_LIMIT
    return limit

# Get model classes (member sponsorship endpoints use sponsoredLegislation / cosponsoredLegislation keys)
SponsoredLegislationModel = ModelRegistry.get_model("SponsoredLegislation")
CosponsoredLegislationModel = ModelRegistry.get_model("CosponsoredLegislation")


def _get_member_config():
    """Lazy import of member expansion configuration."""
    from congressgov.services.member import MEMBER_MAPPINGS, MEMBER_PARAMETERS
    return MEMBER_MAPPINGS, MEMBER_PARAMETERS


@register_method(Member)
def expand(
    self,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> Member:
    """
    Expand attributes of this Member instance by fetching related data from the API.

    Replaces count stubs on the member detail (if present) with full
    ``SponsoredLegislation`` / ``CosponsoredLegislation`` payloads.

    Args:
        client: API client. If None, uses ``self.client`` when available.
        attributes: Attributes to expand. If None, expands all mapped attributes.
        **kwargs: Passed to sponsorship list API functions (e.g. offset, limit, format_).

    Returns:
        A deepcopy of this member with expanded attributes set.

    Raises:
        ValueError: If ``bioguideId`` is missing.

    Examples:
        >>> expanded = member.expand(client=my_client)
        >>> expanded = member.expand(attributes=["sponsoredLegislation"])
    """
    MEMBER_MAPPINGS, MEMBER_PARAMETERS = _get_member_config()
    return expand_sync_instance(
        self,
        mapping=MEMBER_MAPPINGS,
        parameters=MEMBER_PARAMETERS,
        client=client,
        attributes=attributes,
        entity_name="Member",
        **kwargs,
    )


@register_method(Member)
def expand_specific_attributes(
    self,
    *attributes: str,
    client: Any = None,
    **kwargs: Any,
) -> Member:
    """Expand only the given attributes (varargs)."""
    return self.expand(client=client, attributes=list(attributes), **kwargs)


@register_method(Member)
def get_available_attributes(self) -> list[str]:
    """List attribute names that ``expand()`` can populate."""
    MEMBER_MAPPINGS, _ = _get_member_config()
    return list(MEMBER_MAPPINGS.keys())


def _member_sponsorship_params(self) -> dict[str, Any]:
    """Internal helper -- called directly, not as a bound Member method."""
    _, MEMBER_PARAMETERS = _get_member_config()
    return extract_parameters_from_target(self, MEMBER_PARAMETERS)


@register_method(Member)
def get_sponsored_legislation(
    self,
    client: Any = None,
    format_: str = None,
    offset: int = None,
    limit: int | str = None,
    *,
    refresh: bool = False,
) -> Any:
    """
    Load sponsored legislation for this member into ``sponsoredLegislation``.

    Fetches from the API when the attribute is missing or still a count stub
    (``CountRef``). Reuses a previously loaded ``SponsoredLegislation`` unless
    ``refresh=True``.

    The client is taken from ``self.client``, or from the parent ``Members``
    collection when this member came from a list/search.

    Args:
        client: API client override.
        format_: Response format (default: json).
        offset: Number of records to skip.
        limit: Maximum number of records (``int``), or ``'max'`` for 250 (API cap).
        refresh: If True, always refetch even when already loaded.

    Returns:
        ``self.sponsoredLegislation`` after fetch (``SponsoredLegislation`` model).

    Example:
        >>> member = member_service.get(bioguide_id="A000374")
        >>> sponsored = member.get_sponsored_legislation()
        >>> assert member.sponsoredLegislation is sponsored
    """
    return bind_related_attribute(
        self,
        attribute_name="sponsoredLegislation",
        model_class=SponsoredLegislationModel,
        api_function=member_sponsorship_list_sync,
        client=client,
        api_params=_member_sponsorship_params(self),
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=_coerce_sponsorship_limit(limit),
    )


@register_method(Member)
def get_cosponsored_legislation(
    self,
    client: Any = None,
    format_: str = None,
    offset: int = None,
    limit: int | str = None,
    *,
    refresh: bool = False,
) -> Any:
    """
    Load cosponsored legislation for this member into ``cosponsoredLegislation``.

    Same behavior as :meth:`get_sponsored_legislation` for the cosponsor endpoint.

    Returns:
        ``self.cosponsoredLegislation`` after fetch (``CosponsoredLegislation`` model).
    """
    return bind_related_attribute(
        self,
        attribute_name="cosponsoredLegislation",
        model_class=CosponsoredLegislationModel,
        api_function=member_cosponsorship_list_sync,
        client=client,
        api_params=_member_sponsorship_params(self),
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=_coerce_sponsorship_limit(limit),
    )