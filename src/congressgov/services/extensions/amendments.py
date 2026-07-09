"""
Query and convenience methods for the Amendments model.

Registered dynamically via ``_registry`` so Amendments stay plain data models.

Field Mappings:
- type: Supports both codes ("hamdt", "samdt") and full names
  Uses LegislationType enum for automatic expansion (if available)

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_type(), by_congress(), by_chamber(), etc.
- Utility methods: house_amendments(), senate_amendments()
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.amendment import Amendments, Amendment

# Import the actual class for registration
from congressgov.models.entities.amendment import Amendments
import congressgov.models.entities.amendment as amendment_module

# Import Amendment class for validation
from congressgov.models.entities.amendment import Amendment


AmendmentsQuery = create_query_builder(
    collection_class=Amendments,
    items_field="amendments",
    item_class=Amendment,
    field_mappings={
        # Example: "type": FieldMapping(enum_class=AmendmentType)
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
amendment_module.AmendmentsQuery = AmendmentsQuery

if not TYPE_CHECKING:
    globals()['AmendmentsQuery'] = AmendmentsQuery


@register_method(Amendments)
def query(self):
    """Return a query builder for chained filtering."""
    return AmendmentsQuery(self.amendments or [])


@register_method(Amendments)
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Amendments)
def by_type(self, amendment_type: str) -> Amendments:
    """Get amendments of a specific type."""
    return self.query().filter(type=amendment_type)


@register_method(Amendments)
def by_congress(self, congress: int) -> Amendments:
    """Get amendments from a specific Congress."""
    return self.query().filter(congress=congress)


@register_method(Amendments)
def house_amendments(self) -> Amendments:
    """Get all House amendments (hamdt)."""
    def is_house_amendment(a: Amendment) -> bool:
        if not a.type:
            return False
        amdt_type = a.type.value if hasattr(a.type, 'value') else str(a.type)
        return amdt_type.lower() in ["hamdt"]
    
    return self.query().where(is_house_amendment)


@register_method(Amendments)
def senate_amendments(self) -> Amendments:
    """Get all Senate amendments (samdt, suamdt)."""
    def is_senate_amendment(a: Amendment) -> bool:
        if not a.type:
            return False
        amdt_type = a.type.value if hasattr(a.type, 'value') else str(a.type)
        return amdt_type.lower() in ["samdt", "suamdt"]
    
    return self.query().where(is_senate_amendment)


@register_method(Amendments)
def with_actions(self) -> Amendments:
    """Get amendments that have actions recorded."""
    def has_actions(a: Amendment) -> bool:
        if not hasattr(a, 'actions') or a.actions is None:
            return False
        # Handle CountRef case
        if hasattr(a.actions, 'count'):
            return (a.actions.count or 0) > 0
        # Handle list case
        if isinstance(a.actions, list):
            return len(a.actions) > 0
        return False
    
    return self.query().where(has_actions)


@register_method(Amendments)
def group_by(self, field: str):
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)


import json
from typing import Any, Optional
from congressgov._client.api.amendments import (
    amendment_actions_sync,
    amendment_amendments_sync,
    amendment_cosponsors_sync,
    amendment_text_sync
)
from congressgov.models.base.model import ApiEnvelope
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.expansion_helpers import expand_sync_instance

# Get model classes
ActionsModelSingular = ModelRegistry.get_model("Actions")
AmendmentsModelSingular = ModelRegistry.get_model("Amendments")
CosponsorsModelSingular = ModelRegistry.get_model("Cosponsors")
TextVersionsModelSingular = ModelRegistry.get_model("TextVersions")


def _get_amendment_config():
    """Lazy import of amendment configuration."""
    from congressgov.services.amendment import AMENDMENT_MAPPINGS, AMENDMENT_PARAMETERS
    return AMENDMENT_MAPPINGS, AMENDMENT_PARAMETERS


def _amendment_ids(self: Any) -> tuple[Any, Any, Any]:
    """Extract and normalize (congress, amendment_type, amendment_number) from an Amendment.

    Shared by the sub-resource getters below, which previously repeated this
    extraction/normalization block independently for each sub-resource.
    """
    congress = getattr(self, 'congress', None)
    amendment_type = getattr(self, 'amendment_type', getattr(self, 'type', None))
    amendment_number = getattr(self, 'amendment_number', getattr(self, 'number', None))

    if isinstance(amendment_type, str):
        amendment_type = amendment_type.lower()
    elif hasattr(amendment_type, 'value'):
        amendment_type = str(amendment_type.value).lower()

    return congress, amendment_type, amendment_number


@register_method(Amendment)
def expand(
    self,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any
) -> Amendment:
    """
    Expand attributes of this Amendment instance by fetching additional data.
    
    Args:
        client: API client. If None, uses self.client.
        attributes: Optional list of attributes to expand. If None, expands all.
        **kwargs: Additional arguments for API functions.
        
    Returns:
        Deepcopy of this Amendment with expanded attributes.
        
    Example:
        >>> expanded = amendment.expand(client=my_client, attributes=['actions'])
    """
    AMENDMENT_MAPPINGS, AMENDMENT_PARAMETERS = _get_amendment_config()
    return expand_sync_instance(
        self,
        mapping=AMENDMENT_MAPPINGS,
        parameters=AMENDMENT_PARAMETERS,
        client=client,
        attributes=attributes,
        normalize_params=["amendment_type"],
        entity_name="Amendment",
        **kwargs,
    )


@register_method(Amendment)
def get_actions(self, client: Any = None, **kwargs: Any) -> Any:
    """Get actions for this amendment."""
    resolved_client = ApiService._resolve_client(self, client)
    congress, amendment_type, amendment_number = _amendment_ids(self)

    resp = amendment_actions_sync(
        client=resolved_client,
        congress=congress,
        amendment_type=amendment_type,
        amendment_number=amendment_number,
        **kwargs
    )
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return ActionsModelSingular.model_validate(api_env.data)


@register_method(Amendment)
def get_amendments(self, client: Any = None, **kwargs: Any) -> Any:
    """Get amendments to this amendment."""
    resolved_client = ApiService._resolve_client(self, client)
    congress, amendment_type, amendment_number = _amendment_ids(self)

    resp = amendment_amendments_sync(
        client=resolved_client,
        congress=congress,
        amendment_type=amendment_type,
        amendment_number=amendment_number,
        **kwargs
    )
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return AmendmentsModelSingular.model_validate(api_env.data)


@register_method(Amendment)
def get_cosponsors(self, client: Any = None, **kwargs: Any) -> Any:
    """Get cosponsors for this amendment."""
    resolved_client = ApiService._resolve_client(self, client)
    congress, amendment_type, amendment_number = _amendment_ids(self)

    resp = amendment_cosponsors_sync(
        client=resolved_client,
        congress=congress,
        amendment_type=amendment_type,
        amendment_number=amendment_number,
        **kwargs
    )
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CosponsorsModelSingular.model_validate(api_env.data)


@register_method(Amendment)
def get_text_versions(self, client: Any = None, **kwargs: Any) -> Any:
    """Get text versions for this amendment."""
    resolved_client = ApiService._resolve_client(self, client)
    congress, amendment_type, amendment_number = _amendment_ids(self)

    resp = amendment_text_sync(
        client=resolved_client,
        congress=congress,
        amendment_type=amendment_type,
        amendment_number=amendment_number,
        **kwargs
    )
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return TextVersionsModelSingular.model_validate(api_env.data)


@register_method(Amendment)
def get_available_attributes(self) -> list[str]:
    """Returns list of expandable attributes."""
    AMENDMENT_MAPPINGS, _ = _get_amendment_config()
    return list(AMENDMENT_MAPPINGS.keys())