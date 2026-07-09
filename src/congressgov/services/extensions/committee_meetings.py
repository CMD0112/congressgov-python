"""
Query and convenience methods for the CommitteeMeetings model.

These methods are dynamically registered on the CommitteeMeetings class,
keeping the model file clean and focused on data validation.

The query builder (CommitteeMeetingsQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_congress(), by_chamber(), upcoming(), past(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, date

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.meetings.meeting import CommitteeMeetings, CommitteeMeeting

# Import the actual class for registration
from congressgov.models.meetings.meeting import CommitteeMeetings
import congressgov.models.meetings.meeting as meeting_module

# Import CommitteeMeeting class for validation
from congressgov.models.meetings.meeting import CommitteeMeeting

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the CommitteeMeetingsQuery class using the generic query builder
# NOTE: item_class enables field validation to catch typos early
CommitteeMeetingsQuery = create_query_builder(
    collection_class=CommitteeMeetings,
    items_field="meetings",
    item_class=CommitteeMeeting,
    field_mappings={
        # NOTE: Add field mappings here as enums become available
    }
)

# NOTE: Set it on the module so it can be imported
meeting_module.CommitteeMeetingsQuery = CommitteeMeetingsQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['CommitteeMeetingsQuery'] = CommitteeMeetingsQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(CommitteeMeetings)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        meetings.query().filter(chamber="House", lazy=True).order_by("date").execute()
    
    Returns:
        CommitteeMeetingsQuery instance for chaining operations
    """
    return CommitteeMeetingsQuery(self.meetings or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(CommitteeMeetings)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter committee meetings by field values.
    
    Args:
        lazy: If True, return CommitteeMeetingsQuery for chaining. If False, return CommitteeMeetings object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns CommitteeMeetings object
        house_meetings = meetings.filter(chamber="House")
        
        # Lazy - returns builder for chaining
        query = meetings.filter(chamber="House", lazy=True).order_by("date")
        results = query.execute()
    
    Returns:
        CommitteeMeetings object (if eager) or CommitteeMeetingsQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(CommitteeMeetings)
def by_congress(self, congress: int) -> CommitteeMeetings:
    """
    Get meetings from a specific Congress (always eager, returns CommitteeMeetings).
    
    Args:
        congress: Congress number (e.g., 118 for 118th Congress)
    
    Returns:
        Filtered CommitteeMeetings object
    
    Example:
        congress_118 = meetings.by_congress(118)
    """
    return self.query().filter(congress=congress)


@register_method(CommitteeMeetings)
def by_chamber(self, chamber: str) -> CommitteeMeetings:
    """
    Get meetings from a specific chamber (always eager, returns CommitteeMeetings).
    
    Args:
        chamber: Chamber name ("House", "Senate")
    
    Returns:
        Filtered CommitteeMeetings object
    
    Example:
        house_meetings = meetings.by_chamber("House")
    """
    return self.query().filter(chamber=chamber)


@register_method(CommitteeMeetings)
def upcoming(self, days: int = 30) -> CommitteeMeetings:
    """
    Get meetings scheduled in the next N days (always eager, returns CommitteeMeetings).
    
    Args:
        days: Number of days to look ahead (default: 30)
    
    Returns:
        Filtered CommitteeMeetings object
    
    Example:
        next_week = meetings.upcoming(days=7)
    """
    def is_upcoming(m: CommitteeMeeting) -> bool:
        if not hasattr(m, 'date') or not m.date:
            return False
        
        meeting_date = m.date
        # Handle string dates
        if isinstance(meeting_date, str):
            try:
                meeting_date = datetime.fromisoformat(meeting_date.replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                return False
        # Handle datetime objects
        elif isinstance(meeting_date, datetime):
            meeting_date = meeting_date.date()
        elif not isinstance(meeting_date, date):
            return False
        
        # Check if in the future within N days
        today = date.today()
        days_ahead = (meeting_date - today).days
        return 0 <= days_ahead <= days
    
    return self.query().where(is_upcoming)


@register_method(CommitteeMeetings)
def past(self, days: int = 30) -> CommitteeMeetings:
    """
    Get meetings from the last N days (always eager, returns CommitteeMeetings).
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        Filtered CommitteeMeetings object
    
    Example:
        last_week = meetings.past(days=7)
    """
    def is_past(m: CommitteeMeeting) -> bool:
        if not hasattr(m, 'date') or not m.date:
            return False
        
        meeting_date = m.date
        # Handle string dates
        if isinstance(meeting_date, str):
            try:
                meeting_date = datetime.fromisoformat(meeting_date.replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                return False
        # Handle datetime objects
        elif isinstance(meeting_date, datetime):
            meeting_date = meeting_date.date()
        elif not isinstance(meeting_date, date):
            return False
        
        # Check if in the past within N days
        today = date.today()
        days_ago = (today - meeting_date).days
        return 0 <= days_ago <= days
    
    return self.query().where(is_past)


@register_method(CommitteeMeetings)
def by_committee(self, committee_name: str) -> CommitteeMeetings:
    """
    Get meetings by committee name (partial match, case-insensitive) (always eager, returns CommitteeMeetings).
    
    Args:
        committee_name: Committee name or partial name to search for
    
    Returns:
        Filtered CommitteeMeetings object
    
    Example:
        judiciary = meetings.by_committee("Judiciary")
    """
    def committee_matches(m: CommitteeMeeting) -> bool:
        # Check committees list
        if hasattr(m, 'committees') and m.committees:
            if isinstance(m.committees, list):
                for committee in m.committees:
                    if hasattr(committee, 'name') and committee.name:
                        if committee_name.lower() in committee.name.lower():
                            return True
        return False
    
    return self.query().where(committee_matches)


@register_method(CommitteeMeetings)
def group_by(self, field: str):
    """
    Group committee meetings by field.
    Returns dict mapping field values to CommitteeMeetings objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to CommitteeMeetings objects
    
    Example:
        by_chamber = meetings.group_by("chamber")
    """
    return self.query().group_by(field)

