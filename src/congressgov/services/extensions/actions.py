"""
Query and convenience methods for the Actions model.

These methods are dynamically registered on the Actions class,
keeping the model file clean and focused on data validation.

The query builder (ActionsQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

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

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the ActionsQuery class using the generic query builder
# NOTE: item_class enables field validation to catch typos early
ActionsQuery = create_query_builder(
    collection_class=Actions,
    items_field="actions",
    item_class=Action,
    field_mappings={
        # NOTE: Add field mappings here as enums become available
    }
)

# NOTE: Set it on the module so it can be imported
action_module.ActionsQuery = ActionsQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['ActionsQuery'] = ActionsQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(Actions)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        actions.query().filter(actionCode="H11100", lazy=True).order_by("actionDate").execute()
    
    Returns:
        ActionsQuery instance for chaining operations
    """
    return ActionsQuery(self.actions or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(Actions)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter actions by field values.
    
    Args:
        lazy: If True, return ActionsQuery for chaining. If False, return Actions object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns Actions object
        floor_actions = actions.filter(actionCode="H11100")
        
        # Lazy - returns builder for chaining
        query = actions.filter(actionCode="H11100", lazy=True).order_by("actionDate")
        results = query.execute()
    
    Returns:
        Actions object (if eager) or ActionsQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Actions)
def by_type(self, action_type: str) -> Actions:
    """
    Get actions by type (always eager, returns Actions).
    
    Args:
        action_type: Action type to filter by
    
    Returns:
        Filtered Actions object
    
    Example:
        floor_actions = actions.by_type("Floor")
    """
    return self.query().filter(type=action_type)


@register_method(Actions)
def recent(self, days: int = 30) -> Actions:
    """
    Get actions from the last N days (always eager, returns Actions).
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        Filtered Actions object
    
    Example:
        last_week = actions.recent(days=7)
    """
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
    """
    Group actions by field.
    Returns dict mapping field values to Actions objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to Actions objects
    
    Example:
        by_type = actions.group_by("type")
    """
    return self.query().group_by(field)

