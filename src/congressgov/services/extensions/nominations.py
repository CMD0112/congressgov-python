"""
Query and convenience methods for the Nominations model.

Registered dynamically via ``_registry`` so Nominations stay plain data models.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_congress(), by_organization(), confirmed(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.nominations.nomination import Nominations, Nomination

# Import the actual class for registration
from congressgov.models.nominations.nomination import Nominations
import congressgov.models.nominations.nomination as nomination_module

# Import Nomination class for validation
from congressgov.models.nominations.nomination import Nomination


NominationsQuery = create_query_builder(
    collection_class=Nominations,
    items_field="nominations",
    item_class=Nomination,
    field_mappings={
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
nomination_module.NominationsQuery = NominationsQuery

if not TYPE_CHECKING:
    globals()['NominationsQuery'] = NominationsQuery


@register_method(Nominations)
def query(self):
    """Return a query builder for chained filtering."""
    return NominationsQuery(self.nominations or [])


@register_method(Nominations)
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Nominations)
def by_congress(self, congress: int) -> Nominations:
    """Get nominations from a specific Congress."""
    return self.query().filter(congress=congress)


@register_method(Nominations)
def by_organization(self, organization: str) -> Nominations:
    """Get nominations for a specific organization (partial match, case-insensitive)."""
    def organization_matches(n: Nomination) -> bool:
        if not hasattr(n, 'organization') or not n.organization:
            return False
        return organization.lower() in n.organization.lower()
    
    return self.query().where(organization_matches)


@register_method(Nominations)
def confirmed(self) -> Nominations:
    """Get confirmed nominations."""
    def is_confirmed(n: Nomination) -> bool:
        # Check latest action for confirmation
        if hasattr(n, 'latestAction') and n.latestAction:
            if hasattr(n.latestAction, 'text') and n.latestAction.text:
                text_lower = n.latestAction.text.lower()
                return 'confirmed' in text_lower or 'confirmation' in text_lower
        return False
    
    return self.query().where(is_confirmed)


@register_method(Nominations)
def with_hearings(self) -> Nominations:
    """Get nominations that have hearings scheduled or completed."""
    def has_hearings(n: Nomination) -> bool:
        if not hasattr(n, 'hearings') or n.hearings is None:
            return False
        # Handle CountRef case
        if hasattr(n.hearings, 'count'):
            return (n.hearings.count or 0) > 0
        # Handle list case
        if isinstance(n.hearings, list):
            return len(n.hearings) > 0
        return False
    
    return self.query().where(has_hearings)


@register_method(Nominations)
def group_by(self, field: str):
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)


import json
from typing import Any, Optional
from congressgov._client.api.nomination import (
    nomination_actions_sync,
    nomination_committees_sync,
    nomination_hearings_sync
)
from congressgov.models.base.model import ApiEnvelope
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.expansion_helpers import expand_sync_instance

ActionsModelSingular = ModelRegistry.get_model("Actions")
CommitteesModelSingular = ModelRegistry.get_model("Committees")
HearingsModelSingular = ModelRegistry.get_model("Hearings")


def _get_nomination_config():
    """Lazy import of nomination configuration."""
    from congressgov.services.nomination import NOMINATION_MAPPINGS, NOMINATION_PARAMETERS
    return NOMINATION_MAPPINGS, NOMINATION_PARAMETERS


@register_method(Nomination)
def expand(self, client: Any = None, attributes: Optional[list[str]] = None, **kwargs: Any) -> Nomination:
    """Expand attributes of this Nomination instance."""
    NOMINATION_MAPPINGS, NOMINATION_PARAMETERS = _get_nomination_config()
    return expand_sync_instance(
        self,
        mapping=NOMINATION_MAPPINGS,
        parameters=NOMINATION_PARAMETERS,
        client=client,
        attributes=attributes,
        entity_name="Nomination",
        **kwargs,
    )


@register_method(Nomination)
def get_actions(self, client: Any = None, **kwargs: Any) -> Any:
    """Get actions for this nomination."""
    resolved_client = ApiService._resolve_client(self, client)
    congress = getattr(self, 'congress', None)
    nomination_number = getattr(self, 'nomination_number', getattr(self, 'number', None))
    resp = nomination_actions_sync(client=resolved_client, congress=congress, nomination_number=nomination_number, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return ActionsModelSingular.model_validate(api_env.data)


@register_method(Nomination)
def get_committees(self, client: Any = None, **kwargs: Any) -> Any:
    """Get committees for this nomination."""
    resolved_client = ApiService._resolve_client(self, client)
    congress = getattr(self, 'congress', None)
    nomination_number = getattr(self, 'nomination_number', getattr(self, 'number', None))
    resp = nomination_committees_sync(client=resolved_client, congress=congress, nomination_number=nomination_number, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CommitteesModelSingular.model_validate(api_env.data)


@register_method(Nomination)
def get_hearings(self, client: Any = None, **kwargs: Any) -> Any:
    """Get hearings for this nomination."""
    resolved_client = ApiService._resolve_client(self, client)
    congress = getattr(self, 'congress', None)
    nomination_number = getattr(self, 'nomination_number', getattr(self, 'number', None))
    resp = nomination_hearings_sync(client=resolved_client, congress=congress, nomination_number=nomination_number, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HearingsModelSingular.model_validate(api_env.data)


@register_method(Nomination)
def get_available_attributes(self) -> list[str]:
    """Returns list of expandable attributes."""
    NOMINATION_MAPPINGS, _ = _get_nomination_config()
    return list(NOMINATION_MAPPINGS.keys())