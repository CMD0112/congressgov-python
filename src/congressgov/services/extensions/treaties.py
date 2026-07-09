"""
Query and convenience methods for the Treaties model.

Registered dynamically via ``_registry`` so Treaties stay plain data models.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_congress(), by_topic(), with_actions(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.treaty import Treaties, Treaty

# Import the actual class for registration
from congressgov.models.entities.treaty import Treaties
import congressgov.models.entities.treaty as treaty_module

# Import Treaty class for validation
from congressgov.models.entities.treaty import Treaty


TreatiesQuery = create_query_builder(
    collection_class=Treaties,
    items_field="treaties",
    item_class=Treaty,
    field_mappings={
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
treaty_module.TreatiesQuery = TreatiesQuery

if not TYPE_CHECKING:
    globals()['TreatiesQuery'] = TreatiesQuery


@register_method(Treaties)
def query(self):
    """Return a query builder for chained filtering."""
    return TreatiesQuery(self.treaties or [])


@register_method(Treaties)
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Treaties)
def by_congress(self, congress: int) -> Treaties:
    """Get treaties from a specific Congress."""
    return self.query().filter(congress=congress)


@register_method(Treaties)
def by_topic(self, topic: str) -> Treaties:
    """Get treaties by topic (partial match, case-insensitive)."""
    def topic_matches(t: Treaty) -> bool:
        if hasattr(t, 'topic') and t.topic:
            return topic.lower() in t.topic.lower()
        if hasattr(t, 'title') and t.title:
            return topic.lower() in t.title.lower()
        return False
    
    return self.query().where(topic_matches)


@register_method(Treaties)
def with_actions(self) -> Treaties:
    """Get treaties that have actions recorded."""
    def has_actions(t: Treaty) -> bool:
        if not hasattr(t, 'actions') or t.actions is None:
            return False
        # Handle CountRef case
        if hasattr(t.actions, 'count'):
            return (t.actions.count or 0) > 0
        # Handle list case
        if isinstance(t.actions, list):
            return len(t.actions) > 0
        return False
    
    return self.query().where(has_actions)


@register_method(Treaties)
def ratified(self) -> Treaties:
    """Get ratified treaties."""
    def is_ratified(t: Treaty) -> bool:
        # Check latest action for ratification
        if hasattr(t, 'latestAction') and t.latestAction:
            if hasattr(t.latestAction, 'text') and t.latestAction.text:
                text_lower = t.latestAction.text.lower()
                return 'ratif' in text_lower
        return False
    
    return self.query().where(is_ratified)


@register_method(Treaties)
def group_by(self, field: str):
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)


import json
from typing import Any, Optional
from congressgov._client.api.treaty import (
    treaty_actions_sync,
    treaty_committee_sync
)
from congressgov.models.base.model import ApiEnvelope
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.expansion_helpers import expand_sync_instance

ActionsModelSingular = ModelRegistry.get_model("Actions")
CommitteesModelSingular = ModelRegistry.get_model("Committees")


def _get_treaty_config():
    """Lazy import of treaty configuration."""
    from congressgov.services.treaty import TREATY_MAPPINGS, TREATY_PARAMETERS
    return TREATY_MAPPINGS, TREATY_PARAMETERS


@register_method(Treaty)
def expand(self, client: Any = None, attributes: Optional[list[str]] = None, **kwargs: Any) -> Treaty:
    """Expand attributes of this Treaty instance."""
    TREATY_MAPPINGS, TREATY_PARAMETERS = _get_treaty_config()
    return expand_sync_instance(
        self,
        mapping=TREATY_MAPPINGS,
        parameters=TREATY_PARAMETERS,
        client=client,
        attributes=attributes,
        entity_name="Treaty",
        **kwargs,
    )


@register_method(Treaty)
def get_actions(self, client: Any = None, **kwargs: Any) -> Any:
    """Get actions for this treaty."""
    resolved_client = ApiService._resolve_client(self, client)
    congress = getattr(self, 'congress', None)
    treaty_number = getattr(self, 'treaty_number', getattr(self, 'number', None))
    resp = treaty_actions_sync(client=resolved_client, congress=congress, treaty_number=treaty_number, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return ActionsModelSingular.model_validate(api_env.data)


@register_method(Treaty)
def get_committee(self, client: Any = None, **kwargs: Any) -> Any:
    """Get committee for this treaty."""
    resolved_client = ApiService._resolve_client(self, client)
    congress = getattr(self, 'congress', None)
    treaty_number = getattr(self, 'treaty_number', getattr(self, 'number', None))
    resp = treaty_committee_sync(client=resolved_client, congress=congress, treaty_number=treaty_number, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CommitteesModelSingular.model_validate(api_env.data)


@register_method(Treaty)
def get_available_attributes(self) -> list[str]:
    """Returns list of expandable attributes."""
    TREATY_MAPPINGS, _ = _get_treaty_config()
    return list(TREATY_MAPPINGS.keys())