"""Query helpers for member sponsorship legislation envelopes."""

from __future__ import annotations

from congressgov.models.base.enums import LegislationType
from congressgov.models.entities.member import (
    CosponsoredLegislation,
    CosponsoredLegislationItem,
    SponsoredLegislation,
    SponsoredLegislationItem,
)
import congressgov.models.entities.member as member_module

from ._query_builder import FieldMapping, create_query_builder
from ._registry import register_method

_TYPE_MAPPING = {"type": FieldMapping(enum_class=LegislationType)}


def _register_sponsorship_queries(
    collection_class: type,
    item_class: type,
    items_field: str,
    query_attr: str,
) -> None:
    query_class = create_query_builder(
        collection_class=collection_class,
        items_field=items_field,
        item_class=item_class,
        field_mappings=_TYPE_MAPPING,
    )
    setattr(member_module, query_attr, query_class)

    @register_method(collection_class)
    def query(self):
        """Return a query builder over the legislation items."""
        items = getattr(self, items_field) or []
        return query_class(items)

    @register_method(collection_class)
    def filter(self, *, lazy: bool = False, **kwargs):
        """Filter legislation items (eager by default)."""
        return self.query().filter(lazy=lazy, **kwargs)

    @register_method(collection_class)
    def group_by(self, field: str):
        """Group items by field into new envelope instances."""
        return self.query().group_by(field)


_register_sponsorship_queries(
    SponsoredLegislation,
    SponsoredLegislationItem,
    "sponsoredLegislation",
    "SponsoredLegislationQuery",
)
_register_sponsorship_queries(
    CosponsoredLegislation,
    CosponsoredLegislationItem,
    "cosponsoredLegislation",
    "CosponsoredLegislationQuery",
)
