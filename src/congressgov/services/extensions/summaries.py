"""
Query and convenience methods for the Summaries model.

These methods are dynamically registered on the Summaries class,
keeping the model file clean and focused on data validation.

The query builder (SummariesQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

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

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the SummariesQuery class using the generic query builder
# NOTE: item_class enables field validation to catch typos early
SummariesQuery = create_query_builder(
    collection_class=Summaries,
    items_field="summaries",
    item_class=Summary,
    field_mappings={
        # NOTE: Add field mappings here as enums become available
    }
)

# NOTE: Set it on the module so it can be imported
bill_module.SummariesQuery = SummariesQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['SummariesQuery'] = SummariesQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(Summaries)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        summaries.query().filter(versionCode="00", lazy=True).order_by("actionDate").execute()
    
    Returns:
        SummariesQuery instance for chaining operations
    """
    return SummariesQuery(self.summaries or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(Summaries)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter summaries by field values.
    
    Args:
        lazy: If True, return SummariesQuery for chaining. If False, return Summaries object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns Summaries object
        introduced = summaries.filter(versionCode="00")
        
        # Lazy - returns builder for chaining
        query = summaries.filter(versionCode="00", lazy=True).order_by("actionDate")
        results = query.execute()
    
    Returns:
        Summaries object (if eager) or SummariesQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Summaries)
def by_version(self, version_code: str) -> Summaries:
    """
    Get summaries for a specific bill version (always eager, returns Summaries).
    
    Args:
        version_code: Version code (e.g., "00" for introduced, "49" for public law)
    
    Returns:
        Filtered Summaries object
    
    Example:
        introduced = summaries.by_version("00")
    """
    return self.query().filter(versionCode=version_code)


@register_method(Summaries)
def recent(self, days: int = 30) -> Summaries:
    """
    Get summaries from the last N days (always eager, returns Summaries).
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        Filtered Summaries object
    
    Example:
        last_week = summaries.recent(days=7)
    """
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
    """
    Group summaries by field.
    Returns dict mapping field values to Summaries objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to Summaries objects
    
    Example:
        by_version = summaries.group_by("versionCode")
    """
    return self.query().group_by(field)

