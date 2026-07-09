"""
Query methods for [ModelName] model.

=====================================================================
TEMPLATE FILE - DO NOT USE DIRECTLY - COPY AND CUSTOMIZE
=====================================================================

This file is a template for creating new extension modules. It is NOT
executed or imported directly. Keep it updated as the extension pattern
evolves to serve as documentation and a starting point for new extensions.

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

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the query class using the generic query builder
# NOTE: Field mappings enable shorthand queries using existing enums
# NOTE: item_class enables field validation to catch typos early
[ModelName]Query = create_query_builder(
    collection_class=[ModelName],
    items_field="[items_field]",  # e.g., "bills", "committees", "members"
    item_class=[ModelItem],  # e.g., Bill, Committee, Member
    field_mappings={
        # NOTE: Add field mappings for shorthand support
        # Example: "state": FieldMapping(enum_class=StateCode),
        # This allows: items.filter(state="CA") to match state="California"
    }
)

# NOTE: Set it on the module so it can be imported
model_module.[ModelName]Query = [ModelName]Query

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['[ModelName]Query'] = [ModelName]Query


# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method([ModelName])
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        items.query().filter(field="value", lazy=True).order_by("field").execute()
    
    Returns:
        Query builder instance for this collection
    """
    # Replace 'items' with your actual field name (e.g., 'members', 'bills', 'committees')
    return [ModelName]Query(self.[items_field] or [])


# ========================================
# CONVENIENCE METHODS
# ========================================

@register_method([ModelName])
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter items by field values.
    
    Args:
        lazy: If True, return query builder. If False, return model instance (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Returns:
        [ModelName] object (if eager) or [ModelName]Query (if lazy)
    
    Examples:
        # Eager (default)
        filtered = items.filter(field="value")
        
        # Lazy (for chaining)
        filtered = items.filter(field="value", lazy=True).order_by("field").execute()
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method([ModelName])
def by_field(self, value: str) -> [ModelName]:
    """
    Get items by specific field value.
    
    Args:
        value: The value to filter by
    
    Returns:
        Filtered model instance
    """
    return self.query().filter(field=value)


@register_method([ModelName])
def group_by(self, field: str):
    """
    Group items by field value.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to [ModelName] instances
    
    Example:
        by_field = items.group_by("field")
        # Returns: {"value1": [ModelName](...), "value2": [ModelName](...)}
    """
    return self.query().group_by(field)


# ========================================
# ADD YOUR CUSTOM METHODS BELOW
# ========================================

# Example custom method:
# @register_method([ModelName])
# def my_custom_method(self, arg: str) -> [ModelName]:
#     """Custom method description."""
#     return self.filter(custom_field=arg)

