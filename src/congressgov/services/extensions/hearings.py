"""
Query and convenience methods for the Hearings model.

These methods are dynamically registered on the Hearings class,
keeping the model file clean and focused on data validation.

The query builder (HearingsQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_congress(), by_chamber(), recent(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, date

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.documents.hearing import Hearings, Hearing

# Import the actual class for registration
from congressgov.models.documents.hearing import Hearings
import congressgov.models.documents.hearing as hearing_module

# Import Hearing class for validation
from congressgov.models.documents.hearing import Hearing

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the HearingsQuery class using the generic query builder
# NOTE: item_class enables field validation to catch typos early
HearingsQuery = create_query_builder(
    collection_class=Hearings,
    items_field="hearings",
    item_class=Hearing,
    field_mappings={
        # NOTE: Add field mappings here as enums become available
    }
)

# NOTE: Set it on the module so it can be imported
hearing_module.HearingsQuery = HearingsQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['HearingsQuery'] = HearingsQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(Hearings)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        hearings.query().filter(chamber="House", lazy=True).order_by("date").execute()
    
    Returns:
        HearingsQuery instance for chaining operations
    """
    return HearingsQuery(self.hearings or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(Hearings)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter hearings by field values.
    
    Args:
        lazy: If True, return HearingsQuery for chaining. If False, return Hearings object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns Hearings object
        house_hearings = hearings.filter(chamber="House")
        
        # Lazy - returns builder for chaining
        query = hearings.filter(chamber="House", lazy=True).order_by("date")
        results = query.execute()
    
    Returns:
        Hearings object (if eager) or HearingsQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Hearings)
def by_congress(self, congress: int) -> Hearings:
    """
    Get hearings from a specific Congress (always eager, returns Hearings).
    
    Args:
        congress: Congress number (e.g., 118 for 118th Congress)
    
    Returns:
        Filtered Hearings object
    
    Example:
        congress_118 = hearings.by_congress(118)
    """
    return self.query().filter(congress=congress)


@register_method(Hearings)
def by_chamber(self, chamber: str) -> Hearings:
    """
    Get hearings from a specific chamber (always eager, returns Hearings).
    
    Args:
        chamber: Chamber name ("House", "Senate")
    
    Returns:
        Filtered Hearings object
    
    Example:
        house_hearings = hearings.by_chamber("House")
    """
    return self.query().filter(chamber=chamber)


@register_method(Hearings)
def recent(self, days: int = 30) -> Hearings:
    """
    Get hearings from the last N days (always eager, returns Hearings).
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        Filtered Hearings object
    
    Example:
        last_week = hearings.recent(days=7)
    """
    def is_recent(h: Hearing) -> bool:
        if not hasattr(h, 'date') or not h.date:
            return False
        
        hearing_date = h.date
        # Handle string dates
        if isinstance(hearing_date, str):
            try:
                hearing_date = datetime.fromisoformat(hearing_date.replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                return False
        # Handle datetime objects
        elif isinstance(hearing_date, datetime):
            hearing_date = hearing_date.date()
        elif not isinstance(hearing_date, date):
            return False
        
        # Calculate days ago
        today = date.today()
        days_ago = (today - hearing_date).days
        return days_ago <= days
    
    return self.query().where(is_recent)


@register_method(Hearings)
def by_committee(self, committee_name: str) -> Hearings:
    """
    Get hearings by committee name (partial match, case-insensitive) (always eager, returns Hearings).
    
    Args:
        committee_name: Committee name or partial name to search for
    
    Returns:
        Filtered Hearings object
    
    Example:
        judiciary = hearings.by_committee("Judiciary")
    """
    def committee_matches(h: Hearing) -> bool:
        # Check committees list
        if hasattr(h, 'committees') and h.committees:
            if isinstance(h.committees, list):
                for committee in h.committees:
                    if hasattr(committee, 'name') and committee.name:
                        if committee_name.lower() in committee.name.lower():
                            return True
        return False
    
    return self.query().where(committee_matches)


@register_method(Hearings)
def group_by(self, field: str):
    """
    Group hearings by field.
    Returns dict mapping field values to Hearings objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to Hearings objects
    
    Example:
        by_chamber = hearings.group_by("chamber")
        # Returns: {"House": Hearings(...), "Senate": Hearings(...)}
    """
    return self.query().group_by(field)

