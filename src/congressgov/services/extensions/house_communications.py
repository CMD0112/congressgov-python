"""
Query and convenience methods for the HouseCommunications model.

These methods are dynamically registered on the HouseCommunications class,
keeping the model file clean and focused on data validation.

The query builder (HouseCommunicationsQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

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
    from congressgov.models.communications.house_communication import HouseCommunications, HouseCommunication

# Import the actual class for registration
from congressgov.models.communications.house_communication import HouseCommunications
import congressgov.models.communications.house_communication as house_comm_module

# Import HouseCommunication class for validation
from congressgov.models.communications.house_communication import HouseCommunication

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the HouseCommunicationsQuery class using the generic query builder
# NOTE: item_class enables field validation to catch typos early
HouseCommunicationsQuery = create_query_builder(
    collection_class=HouseCommunications,
    items_field="houseCommunications",
    item_class=HouseCommunication,
    field_mappings={
        # NOTE: Add field mappings here as enums become available
    }
)

# NOTE: Set it on the module so it can be imported
house_comm_module.HouseCommunicationsQuery = HouseCommunicationsQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['HouseCommunicationsQuery'] = HouseCommunicationsQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(HouseCommunications)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        comms.query().filter(congress=118, lazy=True).order_by("number").execute()
    
    Returns:
        HouseCommunicationsQuery instance for chaining operations
    """
    return HouseCommunicationsQuery(self.houseCommunications or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(HouseCommunications)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter house communications by field values.
    
    Args:
        lazy: If True, return HouseCommunicationsQuery for chaining. If False, return HouseCommunications object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns HouseCommunications object
        congress_118 = comms.filter(congress=118)
        
        # Lazy - returns builder for chaining
        query = comms.filter(congress=118, lazy=True).order_by("number")
        results = query.execute()
    
    Returns:
        HouseCommunications object (if eager) or HouseCommunicationsQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(HouseCommunications)
def by_congress(self, congress: int) -> HouseCommunications:
    """
    Get communications from a specific Congress (always eager, returns HouseCommunications).
    
    Args:
        congress: Congress number (e.g., 118 for 118th Congress)
    
    Returns:
        Filtered HouseCommunications object
    
    Example:
        congress_118 = comms.by_congress(118)
    """
    return self.query().filter(congress=congress)


@register_method(HouseCommunications)
def by_type(self, comm_type: str) -> HouseCommunications:
    """
    Get communications of a specific type (always eager, returns HouseCommunications).
    
    Args:
        comm_type: Communication type to filter by
    
    Returns:
        Filtered HouseCommunications object
    
    Example:
        executive = comms.by_type("EC")
    """
    return self.query().filter(type=comm_type)


@register_method(HouseCommunications)
def recent(self, days: int = 30) -> HouseCommunications:
    """
    Get communications from the last N days (always eager, returns HouseCommunications).
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        Filtered HouseCommunications object
    
    Example:
        last_week = comms.recent(days=7)
    """
    def is_recent(c: HouseCommunication) -> bool:
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


@register_method(HouseCommunications)
def group_by(self, field: str):
    """
    Group house communications by field.
    Returns dict mapping field values to HouseCommunications objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to HouseCommunications objects
    
    Example:
        by_type = comms.group_by("type")
    """
    return self.query().group_by(field)

