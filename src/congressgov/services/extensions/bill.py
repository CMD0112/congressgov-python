"""
Query and convenience methods for the Bill and Bills models.

Registered dynamically via ``_registry`` so Bill and Bills stay plain data models.

Field Mappings:
- type: Supports both codes ("hr") and full names ("HR")
  Uses LegislationType enum for automatic expansion
- originChamber: Supports chamber variations ("House", "H", "House of Representatives")
  Uses Chamber enum for automatic expansion

Methods registered on Bills (collection):
- Query methods: filter(), query(), group_by()
- Convenience methods: by_type(), by_congress(), by_chamber(), etc.
- Utility methods: enacted(), house_bills(), senate_bills()
- List as plain list: query().to_list()
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__ (collections_registry)

Methods registered on Bill (singular instance):
- expand(): Expand bill attributes (actions, amendments, committees, etc.)
- expand_specific_attributes(): Expand only specific attributes
- get_available_attributes(): List expandable attributes
- get_actions(), get_amendments(), get_committees(): Fetch related data
- get_cosponsors(), get_related_bills(), get_subjects(), get_summaries()
- get_text_versions(), get_titles()
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from ._registry import register_method
from ._query_builder import create_query_builder, FieldMapping

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.bill import Bills, Bill

# Import the actual classes for registration
from congressgov.models.entities.bill import Bills, Bill
import congressgov.models.entities.bill as bill_module

# Import enums for field mapping
from congressgov.models.base.enums import LegislationType, Chamber

# Import API functions and models for Bill instance methods
from congressgov._client.api.bill import (
    bill_actions_sync,
    bill_amendments_sync,
    bill_committees_sync,
    bill_cosponsors_sync,
    bill_relatedbills_sync,
    bill_subjects_sync,
    bill_summaries_sync,
    bill_text_sync,
    bill_titles_sync
)
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.expansion_helpers import (
    assign_collection_items_to_attribute,
    bind_bill_subresource,
    expand_sync_instance,
)
from congressgov.services.core.api_service import ApiService

def _get_bill_config():
    """Lazily import BILL_MAPPINGS/BILL_PARAMETERS to avoid a circular import with congressgov.services.bill."""
    from congressgov.services.bill import BILL_MAPPINGS, BILL_PARAMETERS
    return BILL_MAPPINGS, BILL_PARAMETERS

ActionsModel = ModelRegistry.get_model("Actions")
AmendmentsModel = ModelRegistry.get_model("Amendments")


def _normalize_bill_amendments(bill: Bill, client: Any = None) -> None:
    """Store ``list[Amendment]`` on ``bill.amendments`` when expand fetched a wrapper."""
    value = getattr(bill, "amendments", None)
    if value is None or isinstance(value, list):
        return
    resolved_client = ApiService._resolve_client(bill, client)
    assign_collection_items_to_attribute(
        bill,
        attribute_name="amendments",
        wrapper=value,
        items_field="amendments",
        client=resolved_client,
    )


def _post_expand_bill(bill: Bill, client: Any = None) -> None:
    _normalize_bill_amendments(bill, client)


CommitteesModel = ModelRegistry.get_model("Committees")
CosponsorsModel = ModelRegistry.get_model("Cosponsors")
BillsModel = ModelRegistry.get_model("Bills")
SubjectModel = ModelRegistry.get_model("Subject")
SummariesModel = ModelRegistry.get_model("Summaries")
TextVersionsModel = ModelRegistry.get_model("TextVersions")
TitlesModel = ModelRegistry.get_model("Titles")


# Import Bill class for validation

BillsQuery = create_query_builder(
    collection_class=Bills,
    items_field="bills",
    item_class=Bill,
    field_mappings={
        "type": FieldMapping(enum_class=LegislationType),
        "originChamber": FieldMapping(enum_class=Chamber),
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
bill_module.BillsQuery = BillsQuery

if not TYPE_CHECKING:
    globals()['BillsQuery'] = BillsQuery


@register_method(Bills)
def query(self):
    """Return a query builder for chained filtering."""
    return BillsQuery(self.bills or [])


@register_method(Bills)
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    if not isinstance(lazy, bool):
        raise TypeError(
            f"filter() 'lazy' parameter must be a boolean, got {type(lazy).__name__}. "
            f"If you're trying to pass a lambda or function, use .query().where() instead: "
            f"bills.query().where(lambda bill: ...)"
        )

    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Bills)
def by_type(self, bill_type: str) -> Bills:
    """Get bills of a specific type."""
    return self.query().filter(type=bill_type)


@register_method(Bills)
def by_congress(self, congress: int) -> Bills:
    """Get bills from a specific Congress."""
    return self.query().filter(congress=congress)


@register_method(Bills)
def by_chamber(self, chamber: str) -> Bills:
    """Get bills by originating chamber."""
    return self.query().filter(originChamber=chamber)


@register_method(Bills)
def house_bills(self) -> Bills:
    """Get all House bills (hr, hres, hjres, hconres)."""
    def is_house_bill(b: Bill) -> bool:
        if not b.type:
            return False
        bill_type = b.type.value if hasattr(b.type, 'value') else str(b.type)
        return bill_type.upper() in ["HR", "HRES", "HJRES", "HCONRES"]
    
    return self.query().where(is_house_bill)


@register_method(Bills)
def senate_bills(self) -> Bills:
    """Get all Senate bills (s, sres, sjres, sconres)."""
    def is_senate_bill(b: Bill) -> bool:
        if not b.type:
            return False
        bill_type = b.type.value if hasattr(b.type, 'value') else str(b.type)
        return bill_type.upper() in ["S", "SRES", "SJRES", "SCONRES"]
    
    return self.query().where(is_senate_bill)


@register_method(Bills)
def resolutions(self) -> Bills:
    """Get all resolutions (hres, sres, hjres, sjres, hconres, sconres)."""
    def is_resolution(b: Bill) -> bool:
        if not b.type:
            return False
        bill_type = b.type.value if hasattr(b.type, 'value') else str(b.type)
        return "RES" in bill_type.upper()
    
    return self.query().where(is_resolution)


@register_method(Bills)
def joint_resolutions(self) -> Bills:
    """Get joint resolutions only (hjres, sjres)."""
    def is_joint_resolution(b: Bill) -> bool:
        if not b.type:
            return False
        bill_type = b.type.value if hasattr(b.type, 'value') else str(b.type)
        return bill_type.upper() in ["HJRES", "SJRES"]
    
    return self.query().where(is_joint_resolution)


@register_method(Bills)
def enacted(self) -> Bills:
    """Get bills that became law (have laws attribute populated)."""
    def has_laws(b: Bill) -> bool:
        # Check if the bill has laws associated with it
        if not hasattr(b, 'laws') or b.laws is None:
            return False
        # Handle CountRef case (has count attribute)
        if hasattr(b.laws, 'count'):
            return (b.laws.count or 0) > 0
        # Handle list case
        if isinstance(b.laws, list):
            return len(b.laws) > 0
        return False
    
    return self.query().where(has_laws)


@register_method(Bills)
def with_actions(self) -> Bills:
    """Get bills that have actions recorded."""
    def has_actions(b: Bill) -> bool:
        if not hasattr(b, 'actions') or b.actions is None:
            return False
        # Handle CountRef case
        if hasattr(b.actions, 'count'):
            return (b.actions.count or 0) > 0
        # Handle list case
        if isinstance(b.actions, list):
            return len(b.actions) > 0
        return False
    
    return self.query().where(has_actions)


@register_method(Bills)
def by_sponsor(self, sponsor_name: str) -> Bills:
    """Get bills by sponsor name (partial match, case-insensitive)."""
    def has_sponsor(b: Bill) -> bool:
        if not hasattr(b, 'sponsors') or not b.sponsors:
            return False
        # Handle list of sponsors
        if isinstance(b.sponsors, list):
            for sponsor in b.sponsors:
                if hasattr(sponsor, 'fullName') and sponsor.fullName:
                    if sponsor_name.lower() in sponsor.fullName.lower():
                        return True
                # Also check firstName and lastName
                if hasattr(sponsor, 'firstName') and sponsor.firstName:
                    if sponsor_name.lower() in sponsor.firstName.lower():
                        return True
                if hasattr(sponsor, 'lastName') and sponsor.lastName:
                    if sponsor_name.lower() in sponsor.lastName.lower():
                        return True
        return False
    
    return self.query().where(has_sponsor)


@register_method(Bills)
def group_by(self, field: str):
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)


# The remaining methods operate on individual Bill instances, fetching
# related sub-resources from the API on demand.


@register_method(Bill)
def expand(
    self: 'Bill',
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any
) -> 'Bill':
    """Fetch related data (actions, amendments, committees, etc.) and return a
    deepcopy of this Bill with those attributes populated.

    Pass ``attributes`` to expand only specific ones; otherwise all mapped
    attributes are expanded. Uses ``self.client`` when ``client`` is omitted.

    Raises:
        ValueError: If congress/bill_type/bill_number can't be resolved.
    """
    BILL_MAPPINGS, BILL_PARAMETERS = _get_bill_config()
    return expand_sync_instance(
        self,
        mapping=BILL_MAPPINGS,
        parameters=BILL_PARAMETERS,
        client=client,
        attributes=attributes,
        normalize_params=["bill_type"],
        entity_name="Bill",
        post_expand=_post_expand_bill,
        **kwargs,
    )


@register_method(Bill)
def expand_specific_attributes(
    self: 'Bill',
    *attributes: str,
    client: Any = None,
    **kwargs: Any
) -> 'Bill':
    """Expand only the given attributes (varargs), e.g. ``bill.expand_specific_attributes('actions', 'cosponsors')``."""
    return self.expand(client=client, attributes=list(attributes), **kwargs)


@register_method(Bill)
def get_available_attributes(self) -> list[str]:
    """List attribute names that ``expand()`` can populate (actions, amendments, committees, ...)."""
    BILL_MAPPINGS, _ = _get_bill_config()
    return list(BILL_MAPPINGS.keys())


@register_method(Bill)
def get_actions(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'ActionsModel':
    """Load this bill's legislative actions (introductions, referrals, votes,
    passage) into ``bill.actions``. Reuses cached results unless refresh=True."""
    return bind_bill_subresource(
        self,
        attribute_name="actions",
        model_class=ActionsModel,
        api_function=bill_actions_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_method(Bill)
def get_amendments(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> list[Any]:
    """Load this bill's amendments (proposed during markup or floor
    consideration) into ``bill.amendments`` as a ``list[Amendment]``."""
    from congressgov.models.base.types import CountRef

    current = getattr(self, "amendments", None)
    if not refresh and current is not None and not isinstance(current, CountRef):
        if isinstance(current, list):
            return current
        resolved_client = ApiService._resolve_client(self, client)
        return assign_collection_items_to_attribute(
            self,
            attribute_name="amendments",
            wrapper=current,
            items_field="amendments",
            client=resolved_client,
        )

    wrapper = bind_bill_subresource(
        self,
        attribute_name="amendments",
        model_class=AmendmentsModel,
        api_function=bill_amendments_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
        sort=sort,
        **kwargs,
    )
    resolved_client = ApiService._resolve_client(self, client)
    return assign_collection_items_to_attribute(
        self,
        attribute_name="amendments",
        wrapper=wrapper,
        items_field="amendments",
        client=resolved_client,
    )


@register_method(Bill)
def get_committees(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'CommitteesModel':
    """Load the committees that reviewed this bill into ``bill.committees``."""
    return bind_bill_subresource(
        self,
        attribute_name="committees",
        model_class=CommitteesModel,
        api_function=bill_committees_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_method(Bill)
def get_cosponsors(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'CosponsorsModel':
    """Load this bill's cosponsors (members backing it besides the primary
    sponsor) into ``bill.cosponsors``."""
    return bind_bill_subresource(
        self,
        attribute_name="cosponsors",
        model_class=CosponsorsModel,
        api_function=bill_cosponsors_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
        sort=sort,
        **kwargs,
    )


@register_method(Bill)
def get_related_bills(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'BillsModel':
    """Load bills related to this one into ``bill.relatedBills``."""
    return bind_bill_subresource(
        self,
        attribute_name="relatedBills",
        model_class=BillsModel,
        api_function=bill_relatedbills_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
        sort=sort,
        **kwargs,
    )


@register_method(Bill)
def get_subjects(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'SubjectModel':
    """Load this bill's policy subjects into ``bill.subjects``."""
    return bind_bill_subresource(
        self,
        attribute_name="subjects",
        model_class=SubjectModel,
        api_function=bill_subjects_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
        sort=sort,
        **kwargs,
    )


@register_method(Bill)
def get_summaries(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'SummariesModel':
    """Load CRS summaries of this bill into ``bill.summaries``."""
    return bind_bill_subresource(
        self,
        attribute_name="summaries",
        model_class=SummariesModel,
        api_function=bill_summaries_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
        sort=sort,
        **kwargs,
    )


@register_method(Bill)
def get_text_versions(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'TextVersionsModel':
    """Load this bill's available text versions into ``bill.textVersions``."""
    return bind_bill_subresource(
        self,
        attribute_name="textVersions",
        model_class=TextVersionsModel,
        api_function=bill_text_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_method(Bill)
def get_titles(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'TitlesModel':
    """Load this bill's alternate/official titles into ``bill.titles``."""
    return bind_bill_subresource(
        self,
        attribute_name="titles",
        model_class=TitlesModel,
        api_function=bill_titles_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )
