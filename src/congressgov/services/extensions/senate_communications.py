"""
Query and convenience methods for the SenateCommunications model.

Registered dynamically via ``_registry`` so SenateCommunications stay plain data models.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_congress(), by_type(), recent(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, date

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.communications.senate_communication import SenateCommunications, SenateCommunication

# Import the actual class for registration
from congressgov.models.communications.senate_communication import SenateCommunications
import congressgov.models.communications.senate_communication as senate_comm_module

# Import SenateCommunication class for validation
from congressgov.models.communications.senate_communication import SenateCommunication


SenateCommunicationsQuery = create_query_builder(
    collection_class=SenateCommunications,
    items_field="senateCommunications",
    item_class=SenateCommunication,
    field_mappings={
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
senate_comm_module.SenateCommunicationsQuery = SenateCommunicationsQuery

if not TYPE_CHECKING:
    globals()['SenateCommunicationsQuery'] = SenateCommunicationsQuery


@register_method(SenateCommunications)
def query(self):
    """Return a query builder for chained filtering."""
    return SenateCommunicationsQuery(self.senateCommunications or [])


@register_method(SenateCommunications)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter senate communications by field values.
    
    Args:
        lazy: If True, return SenateCommunicationsQuery for chaining. If False, return SenateCommunications object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns SenateCommunications object
        congress_118 = comms.filter(congress=118)
        
        # Lazy - returns builder for chaining
        query = comms.filter(congress=118, lazy=True).order_by("number")
        results = query.execute()
    
    Returns:
        SenateCommunications object (if eager) or SenateCommunicationsQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(SenateCommunications)
def by_congress(self, congress: int) -> SenateCommunications:
    """Get communications from a specific Congress."""
    return self.query().filter(congress=congress)


@register_method(SenateCommunications)
def by_type(self, comm_type: str) -> SenateCommunications:
    """Get communications of a specific type."""
    return self.query().filter(type=comm_type)


@register_method(SenateCommunications)
def recent(self, days: int = 30) -> SenateCommunications:
    """Get communications from the last N days."""
    def is_recent(c: SenateCommunication) -> bool:
        if not hasattr(c, 'communicationDate') or not c.communicationDate:
            return False
        
        comm_date = c.communicationDate
        # Handle string dates
        if isinstance(comm_date, str):
            try:
                comm_date = datetime.fromisoformat(comm_date.replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                return False
        # Handle datetime objects
        elif isinstance(comm_date, datetime):
            comm_date = comm_date.date()
        elif not isinstance(comm_date, date):
            return False
        
        # Calculate days ago
        today = date.today()
        days_ago = (today - comm_date).days
        return days_ago <= days
    
    return self.query().where(is_recent)


@register_method(SenateCommunications)
def group_by(self, field: str):
    """
    Group senate communications by field.
    Returns dict mapping field values to SenateCommunications objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to SenateCommunications objects
    
    Example:
        by_type = comms.group_by("type")
    """
    return self.query().group_by(field)

