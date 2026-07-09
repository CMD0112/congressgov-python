"""
Query and convenience methods for the Cosponsors model.

Registered dynamically via ``_registry`` so Cosponsors stay plain data models.

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

# Cosponsor.party stores the API's single-letter code ("D"/"R"/"I"), not
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


field_mappings = {"party": FieldMapping(expand_value=_expand_party)}
if STATE_ENUM:
    field_mappings["state"] = FieldMapping(enum_class=STATE_ENUM)

CosponsorsQuery = create_query_builder(
    collection_class=Cosponsors,
    items_field="cosponsors",
    item_class=Cosponsor,
    field_mappings=field_mappings
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
sponsor_module.CosponsorsQuery = CosponsorsQuery

if not TYPE_CHECKING:
    globals()['CosponsorsQuery'] = CosponsorsQuery


@register_method(Cosponsors)
def query(self):
    """Return a query builder for chained filtering."""
    return CosponsorsQuery(self.cosponsors or [])


@register_method(Cosponsors)
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Cosponsors)
def by_state(self, state: str) -> Cosponsors:
    """Get cosponsors from a specific state."""
    return self.query().filter(state=state)


@register_method(Cosponsors)
def by_party(self, party: str) -> Cosponsors:
    """Get cosponsors from a specific party."""
    return self.query().filter(party=party)


@register_method(Cosponsors)
def democrats(self) -> Cosponsors:
    """Get all Democratic cosponsors."""
    return self.by_party("Democratic")


@register_method(Cosponsors)
def republicans(self) -> Cosponsors:
    """Get all Republican cosponsors."""
    return self.by_party("Republican")


@register_method(Cosponsors)
def withdrawn(self) -> Cosponsors:
    """Get cosponsors who have withdrawn support."""
    def is_withdrawn(c: Cosponsor) -> bool:
        if hasattr(c, 'sponsorshipWithdrawnDate') and c.sponsorshipWithdrawnDate:
            return True
        return False
    
    return self.query().where(is_withdrawn)


@register_method(Cosponsors)
def active(self) -> Cosponsors:
    """Get cosponsors who have not withdrawn support."""
    def is_active(c: Cosponsor) -> bool:
        if hasattr(c, 'sponsorshipWithdrawnDate') and c.sponsorshipWithdrawnDate:
            return False
        return True
    
    return self.query().where(is_active)


@register_method(Cosponsors)
def group_by(self, field: str):
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)

