"""
Query and convenience methods for the HouseVote and HouseVotes models.

Registered dynamically via ``_registry`` so HouseVote and HouseVotes stay plain data models.

Methods registered on HouseVotes (collection):
- Query methods: filter(), query(), group_by()
- List as plain list: query().to_list()
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__ (collections_registry)

"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ._query_builder import create_query_builder
from ._registry import register_method

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.communications.house_vote import HouseVote, HouseVotes

# Import the actual classes for registration
import congressgov.models.communications.house_vote as housevote_module
from congressgov.models.communications.house_vote import HouseVote, HouseVotes


HouseVotesQuery = create_query_builder(
    collection_class=HouseVotes,
    items_field="houseRollCallVotes",
    item_class=HouseVote,
    field_mappings={},
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
housevote_module.HouseVotesQuery = HouseVotesQuery

if not TYPE_CHECKING:
    globals()["HouseVotesQuery"] = HouseVotesQuery


@register_method(HouseVotes)
def query(self):
    """Return a query builder for chained filtering."""
    return HouseVotesQuery(self.houseRollCallVotes or [])


@register_method(HouseVotes)
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(HouseVotes)
def group_by(self, field: str):
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)
