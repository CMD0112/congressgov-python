"""
Query and convenience methods for the Summaries model.

Registered dynamically via ``_registry`` so Summaries stay plain data models.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_version(), recent(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, date

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.bill import Summaries, Summary

# Import the actual class for registration
from congressgov.models.entities.bill import Summaries
import congressgov.models.entities.bill as bill_module

# Import Summary class for validation
from congressgov.models.entities.bill import Summary


SummariesQuery = create_query_builder(
    collection_class=Summaries,
    items_field="summaries",
    item_class=Summary,
    field_mappings={
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
bill_module.SummariesQuery = SummariesQuery

if not TYPE_CHECKING:
    globals()['SummariesQuery'] = SummariesQuery


@register_method(Summaries)
def query(self):
    """Return a query builder for chained filtering."""
    return SummariesQuery(self.summaries or [])


@register_method(Summaries)
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Summaries)
def by_version(self, version_code: str) -> Summaries:
    """Get summaries for a specific bill version."""
    return self.query().filter(versionCode=version_code)


@register_method(Summaries)
def recent(self, days: int = 30) -> Summaries:
    """Get summaries from the last N days."""
    def is_recent(s: Summary) -> bool:
        if not hasattr(s, 'actionDate') or not s.actionDate:
            return False
        
        action_date = s.actionDate
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


@register_method(Summaries)
def latest(self) -> Summary | None:
    """
    Get the most recent summary by action date.
    
    Returns:
        Most recent Summary object, or None if no summaries
    
    Example:
        latest_summary = summaries.latest()
    """
    if not self.summaries:
        return None
    
    # Sort by actionDate and return the latest
    def get_date(s: Summary):
        if not hasattr(s, 'actionDate') or not s.actionDate:
            return datetime.min.date()
        
        action_date = s.actionDate
        # Handle string dates
        if isinstance(action_date, str):
            try:
                return datetime.fromisoformat(action_date.replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                return datetime.min.date()
        # Handle datetime objects
        elif isinstance(action_date, datetime):
            return action_date.date()
        elif isinstance(action_date, date):
            return action_date
        return datetime.min.date()
    
    return max(self.summaries, key=get_date)


@register_method(Summaries)
def group_by(self, field: str):
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)

