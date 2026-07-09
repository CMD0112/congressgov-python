"""
Query and convenience methods for the Hearings model.

Registered dynamically via ``_registry`` so Hearings stay plain data models.

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


HearingsQuery = create_query_builder(
    collection_class=Hearings,
    items_field="hearings",
    item_class=Hearing,
    field_mappings={
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
hearing_module.HearingsQuery = HearingsQuery

if not TYPE_CHECKING:
    globals()['HearingsQuery'] = HearingsQuery


@register_method(Hearings)
def query(self):
    """Return a query builder for chained filtering."""
    return HearingsQuery(self.hearings or [])


@register_method(Hearings)
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Hearings)
def by_congress(self, congress: int) -> Hearings:
    """Get hearings from a specific Congress."""
    return self.query().filter(congress=congress)


@register_method(Hearings)
def by_chamber(self, chamber: str) -> Hearings:
    """Get hearings from a specific chamber."""
    return self.query().filter(chamber=chamber)


@register_method(Hearings)
def recent(self, days: int = 30) -> Hearings:
    """Get hearings from the last N days."""
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
    """Get hearings by committee name (partial match, case-insensitive)."""
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
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)

