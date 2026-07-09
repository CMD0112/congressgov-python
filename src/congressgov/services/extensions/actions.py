"""
Query and convenience methods for the Actions model.

Registered dynamically via ``_registry`` so Actions stay plain data models.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_type(), by_date(), recent(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, date

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.actions.action import Actions, Action

# Import the actual class for registration
from congressgov.models.actions.action import Actions
import congressgov.models.actions.action as action_module

# Import Action class for validation
from congressgov.models.actions.action import Action


ActionsQuery = create_query_builder(
    collection_class=Actions,
    items_field="actions",
    item_class=Action,
    field_mappings={
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
action_module.ActionsQuery = ActionsQuery

if not TYPE_CHECKING:
    globals()['ActionsQuery'] = ActionsQuery


@register_method(Actions)
def query(self):
    """Return a query builder for chained filtering."""
    return ActionsQuery(self.actions or [])


@register_method(Actions)
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Actions)
def by_type(self, action_type: str) -> Actions:
    """Get actions by type."""
    return self.query().filter(type=action_type)


@register_method(Actions)
def recent(self, days: int = 30) -> Actions:
    """Get actions from the last N days."""
    def is_recent(a: Action) -> bool:
        if not hasattr(a, 'actionDate') or not a.actionDate:
            return False
        
        action_date = a.actionDate
        # Handle string dates
        if isinstance(action_date, str):
            try:
                action_date = datetime.fromisoformat(action_date.replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                return False
        # Handle datetime objects
        elif isinstance(action_date, datetime):
            action_date = action_date.date()
        elif not isinstance(action_date, date):
            return False
        
        # Calculate days ago
        today = date.today()
        days_ago = (today - action_date).days
        return days_ago <= days
    
    return self.query().where(is_recent)


@register_method(Actions)
def group_by(self, field: str):
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)

