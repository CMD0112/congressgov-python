"""Shared list-like protocols for collection wrapper models."""

from __future__ import annotations

from typing import Any, Type

from congressgov.services.extensions._registry import register_method


def _items_list(instance: Any, items_field: str) -> list[Any]:
    return getattr(instance, items_field) or []


def collection_repr(class_name: str, count: int) -> str:
    """Compact repr for list-style API collection wrappers."""
    suffix = "" if count == 1 else "s"
    return f"<{class_name}: {count} item{suffix}>"


def register_collection_protocols(
    collection_class: Type[Any],
    items_field: str,
    *,
    register_repr: bool = True,
) -> None:
    """
    Register ``__iter__``, ``__len__``, ``__getitem__``, and ``__bool__`` on a collection model.

    Use ``collection.query().to_list()`` for a plain ``list`` of items (see ``CollectionQuery``).
    """
    coll = collection_class
    field = items_field

    @register_method(coll, "__iter__")
    def _collection_iter(self: Any):
        return iter(_items_list(self, field))

    @register_method(coll, "__len__")
    def _collection_len(self: Any) -> int:
        return len(_items_list(self, field))

    @register_method(coll, "__getitem__")
    def _collection_getitem(self: Any, key: int | slice) -> Any:
        items = _items_list(self, field)
        result = items[key]
        if isinstance(key, slice):
            return coll(**{field: result})
        return result

    @register_method(coll, "__bool__")
    def _collection_bool(self: Any) -> bool:
        return bool(getattr(self, field))

    if register_repr:

        @register_method(coll, "__repr__")
        def _collection_repr(self: Any) -> str:
            count = len(_items_list(self, field))
            return collection_repr(coll.__name__, count)
