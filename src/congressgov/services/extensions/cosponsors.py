"""
Query and convenience methods for the Cosponsors model.

These methods are dynamically registered on the Cosponsors class,
keeping the model file clean and focused on data validation.

The query builder (CosponsorsQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_state(), by_party(), withdrawn(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ._registry import register_method
from ._query_builder import create_query_builder, FieldMapping

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.sponsor import Cosponsors, Cosponsor

# Import the actual class for registration
from congressgov.models.entities.sponsor import Cosponsors
import congressgov.models.entities.sponsor as sponsor_module

# Import Cosponsor class for validation
from congressgov.models.entities.sponsor import Cosponsor

# Import enum for state code mapping
try:
    from congressgov.models.base.enums import StateCode
    STATE_ENUM = StateCode
except ImportError:
    STATE_ENUM = None

# NOTE: Cosponsor.party stores the API's single-letter code ("D"/"R"/"I"), not
# the full party name. by_party()/democrats()/republicans() pass full names, so
# without this expansion filter(party="Democratic") would silently match nothing.
_PARTY_CODE_TO_NAME = {
    "D": "Democratic",
    "R": "Republican",
    "I": "Independent",
    "ID": "Independent",
    "L": "Libertarian",
}
_PARTY_NAME_TO_CODE = {name.lower(): code for code, name in _PARTY_CODE_TO_NAME.items()}


def _expand_party(value):
    """Expand a party code or name to include both forms (e.g. "D" <-> "Democratic")."""
    if not isinstance(value, str):
        return [value]
    values = [value]
    if value.upper() in _PARTY_CODE_TO_NAME:
        values.append(_PARTY_CODE_TO_NAME[value.upper()])
    if value.lower() in _PARTY_NAME_TO_CODE:
        values.append(_PARTY_NAME_TO_CODE[value.lower()])
    return values


# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the CosponsorsQuery class using the generic query builder
# NOTE: item_class enables field validation to catch typos early
field_mappings = {"party": FieldMapping(expand_value=_expand_party)}
if STATE_ENUM:
    field_mappings["state"] = FieldMapping(enum_class=STATE_ENUM)

CosponsorsQuery = create_query_builder(
    collection_class=Cosponsors,
    items_field="cosponsors",
    item_class=Cosponsor,
    field_mappings=field_mappings
)

# NOTE: Set it on the module so it can be imported
sponsor_module.CosponsorsQuery = CosponsorsQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['CosponsorsQuery'] = CosponsorsQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(Cosponsors)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        cosponsors.query().filter(state="CA", lazy=True).order_by("sponsorshipDate").execute()
    
    Returns:
        CosponsorsQuery instance for chaining operations
    """
    return CosponsorsQuery(self.cosponsors or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(Cosponsors)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter cosponsors by field values.
    
    Args:
        lazy: If True, return CosponsorsQuery for chaining. If False, return Cosponsors object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns Cosponsors object
        ca_cosponsors = cosponsors.filter(state="CA")
        
        # Lazy - returns builder for chaining
        query = cosponsors.filter(state="CA", lazy=True).order_by("sponsorshipDate")
        results = query.execute()
    
    Returns:
        Cosponsors object (if eager) or CosponsorsQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Cosponsors)
def by_state(self, state: str) -> Cosponsors:
    """
    Get cosponsors from a specific state (always eager, returns Cosponsors).
    
    Args:
        state: State code (e.g., "CA") or full name (e.g., "California")
    
    Returns:
        Filtered Cosponsors object
    
    Example:
        ca_cosponsors = cosponsors.by_state("CA")
    """
    return self.query().filter(state=state)


@register_method(Cosponsors)
def by_party(self, party: str) -> Cosponsors:
    """
    Get cosponsors from a specific party (always eager, returns Cosponsors).
    
    Args:
        party: Party name (e.g., "Democratic", "Republican")
    
    Returns:
        Filtered Cosponsors object
    
    Example:
        democrats = cosponsors.by_party("Democratic")
    """
    return self.query().filter(party=party)


@register_method(Cosponsors)
def democrats(self) -> Cosponsors:
    """
    Get all Democratic cosponsors (always eager, returns Cosponsors).
    
    Returns:
        Filtered Cosponsors object
    
    Example:
        democrats = cosponsors.democrats()
    """
    return self.by_party("Democratic")


@register_method(Cosponsors)
def republicans(self) -> Cosponsors:
    """
    Get all Republican cosponsors (always eager, returns Cosponsors).
    
    Returns:
        Filtered Cosponsors object
    
    Example:
        republicans = cosponsors.republicans()
    """
    return self.by_party("Republican")


@register_method(Cosponsors)
def withdrawn(self) -> Cosponsors:
    """
    Get cosponsors who have withdrawn support (always eager, returns Cosponsors).
    
    Returns:
        Filtered Cosponsors object containing only withdrawn cosponsors
    
    Example:
        withdrawn = cosponsors.withdrawn()
    """
    def is_withdrawn(c: Cosponsor) -> bool:
        if hasattr(c, 'sponsorshipWithdrawnDate') and c.sponsorshipWithdrawnDate:
            return True
        return False
    
    return self.query().where(is_withdrawn)


@register_method(Cosponsors)
def active(self) -> Cosponsors:
    """
    Get cosponsors who have not withdrawn support (always eager, returns Cosponsors).
    
    Returns:
        Filtered Cosponsors object containing only active cosponsors
    
    Example:
        active = cosponsors.active()
    """
    def is_active(c: Cosponsor) -> bool:
        if hasattr(c, 'sponsorshipWithdrawnDate') and c.sponsorshipWithdrawnDate:
            return False
        return True
    
    return self.query().where(is_active)


@register_method(Cosponsors)
def group_by(self, field: str):
    """
    Group cosponsors by field.
    Returns dict mapping field values to Cosponsors objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to Cosponsors objects
    
    Example:
        by_state = cosponsors.group_by("state")
        # Returns: {"CA": Cosponsors(...), "NY": Cosponsors(...), ...}
    """
    return self.query().group_by(field)

