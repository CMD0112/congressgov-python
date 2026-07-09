"""
Query methods for [ModelName] model.

TEMPLATE FILE - not executed or imported. Copy it to start a new
extension module and keep it in sync as the extension pattern evolves.

Steps to use this template:
1. Copy this file: cp _template.py mymodel.py
2. Replace [ModelName] with your model class name (e.g., Bills, Committees)
3. Replace [model_path] with the import path (e.g., models.documents.bill)
4. Replace [items_field] with the field name (e.g., "bills", "committees")
5. Replace [ModelItem] with individual item type (e.g., Bill, Committee)
6. Add your custom methods using @register_method decorator
7. Update extensions/__init__.py to import your module

Standard methods to implement:
- query() - Get query builder (use query().to_list() for a plain list)
- filter() - Filter items with lazy option
- group_by() - Group items by field

List-like protocols (__iter__, __len__, __getitem__, __bool__, __repr__) are registered
in collections_registry.py — add your collection there when introducing a new wrapper.

Optional domain-specific methods:
- by_state(), by_chamber(), by_party(), etc.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ._registry import register_method
from ._query_builder import create_query_builder, FieldMapping

# Type hints only - avoids circular imports
if TYPE_CHECKING:
    from [model_path] import [ModelName], [ModelItem]

# Actual import for registration
from [model_path] import [ModelName]
import [model_path] as model_module

# Optional: Import enums for field mappings
# from congressgov.models.base.enums import StateCode, LegislationType, etc.

[ModelName]Query = create_query_builder(
    collection_class=[ModelName],
    items_field="[items_field]",  # e.g., "bills", "committees", "members"
    item_class=[ModelItem],  # e.g., Bill, Committee, Member
    field_mappings={
        # Example: "state": FieldMapping(enum_class=StateCode) lets
        # items.filter(state="CA") also match state="California".
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
model_module.[ModelName]Query = [ModelName]Query

if not TYPE_CHECKING:
    globals()['[ModelName]Query'] = [ModelName]Query


@register_method([ModelName])
def query(self):
    """Return a query builder for chained filtering."""
    # Replace 'items' with your actual field name (e.g., 'members', 'bills', 'committees')
    return [ModelName]Query(self.[items_field] or [])


@register_method([ModelName])
def filter(self, *, lazy: bool = False, **kwargs):
    """Filter by field values; pass lazy=True to keep chaining."""
    return self.query().filter(lazy=lazy, **kwargs)


@register_method([ModelName])
def by_field(self, value: str) -> [ModelName]:
    """Get items matching a specific field value."""
    return self.query().filter(field=value)


@register_method([ModelName])
def group_by(self, field: str):
    """Group items into a dict keyed by field value."""
    return self.query().group_by(field)


# Add custom methods below, e.g.:
# @register_method([ModelName])
# def my_custom_method(self, arg: str) -> [ModelName]:
#     """Custom method description."""
#     return self.filter(custom_field=arg)

