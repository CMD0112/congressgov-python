"""
Query and convenience methods for the Treaties model.

These methods are dynamically registered on the Treaties class,
keeping the model file clean and focused on data validation.

The query builder (TreatiesQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

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

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the TreatiesQuery class using the generic query builder
# NOTE: item_class enables field validation to catch typos early
TreatiesQuery = create_query_builder(
    collection_class=Treaties,
    items_field="treaties",
    item_class=Treaty,
    field_mappings={
        # NOTE: Add field mappings here as enums become available
    }
)

# NOTE: Set it on the module so it can be imported
treaty_module.TreatiesQuery = TreatiesQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['TreatiesQuery'] = TreatiesQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(Treaties)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        treaties.query().filter(congress=118, lazy=True).order_by("number").execute()
    
    Returns:
        TreatiesQuery instance for chaining operations
    """
    return TreatiesQuery(self.treaties or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(Treaties)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter treaties by field values.
    
    Args:
        lazy: If True, return TreatiesQuery for chaining. If False, return Treaties object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns Treaties object
        congress_118 = treaties.filter(congress=118)
        
        # Lazy - returns builder for chaining
        query = treaties.filter(congress=118, lazy=True).order_by("number")
        results = query.execute()
    
    Returns:
        Treaties object (if eager) or TreatiesQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Treaties)
def by_congress(self, congress: int) -> Treaties:
    """
    Get treaties from a specific Congress (always eager, returns Treaties).
    
    Args:
        congress: Congress number (e.g., 118 for 118th Congress)
    
    Returns:
        Filtered Treaties object
    
    Example:
        congress_118 = treaties.by_congress(118)
    """
    return self.query().filter(congress=congress)


@register_method(Treaties)
def by_topic(self, topic: str) -> Treaties:
    """
    Get treaties by topic (partial match, case-insensitive) (always eager, returns Treaties).
    
    Args:
        topic: Topic name or partial name to search for
    
    Returns:
        Filtered Treaties object
    
    Example:
        defense = treaties.by_topic("defense")
    """
    def topic_matches(t: Treaty) -> bool:
        if hasattr(t, 'topic') and t.topic:
            return topic.lower() in t.topic.lower()
        if hasattr(t, 'title') and t.title:
            return topic.lower() in t.title.lower()
        return False
    
    return self.query().where(topic_matches)


@register_method(Treaties)
def with_actions(self) -> Treaties:
    """
    Get treaties that have actions recorded (always eager, returns Treaties).
    
    Returns:
        Filtered Treaties object containing treaties with actions
    
    Example:
        active_treaties = treaties.with_actions()
    """
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
    """
    Get ratified treaties (always eager, returns Treaties).
    
    Returns:
        Filtered Treaties object containing only ratified treaties
    
    Example:
        ratified = treaties.ratified()
    """
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
    """
    Group treaties by field.
    Returns dict mapping field values to Treaties objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to Treaties objects
    
    Example:
        by_congress = treaties.group_by("congress")
    """
    return self.query().group_by(field)


# ========================================
# TREATY (SINGULAR) INSTANCE METHODS
# ========================================

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