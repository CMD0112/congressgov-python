"""
Generic query builder shared by every collection model's extension module.

One `CollectionQuery` implementation backs `Members.query()`, `Bills.query()`,
etc., so each entity doesn't need its own filter/sort/paginate class. Field
mappings let a query value like "CA" also match "California"; field
validation catches typos and suggests corrections via fuzzy matching.
"""
from __future__ import annotations
from typing import Generic, TypeVar, Callable, Any, Iterator, Type
from dataclasses import dataclass
from enum import Enum
from difflib import get_close_matches

# Type variables for generic query builder
ItemT = TypeVar('ItemT')  # Individual item type (Member, Bill, etc.)
CollectionT = TypeVar('CollectionT')  # Collection type (Members, Bills, etc.)


def enum_expander(enum_class: Type[Enum]) -> Callable[[Any], list[Any]]:
    """Build a value expander from an Enum's code/value pairs.

    Example: ``enum_expander(StateCode)("CA")`` returns ``["CA", "California"]``,
    and the reverse lookup works too, so either form matches a query.
    """
    code_to_value = {member.name: member.value for member in enum_class}
    value_to_code = {member.value.lower(): member.name for member in enum_class}

    def expander(query_value: Any) -> list[Any]:
        if not isinstance(query_value, str):
            return [query_value]

        values = [query_value]
        upper_query = query_value.upper()
        lower_query = query_value.lower()

        if upper_query in code_to_value:  # code -> value, e.g. "CA" -> "California"
            values.append(code_to_value[upper_query])

        if lower_query in value_to_code:  # value -> code, e.g. "California" -> "CA"
            values.append(value_to_code[lower_query])

        return values

    return expander


def _comparable_value(value: Any) -> Any:
    """Extract the underlying value from an Enum member for comparison."""
    if isinstance(value, Enum):
        return value.value
    return value


def _values_match(item_value: Any, query_value: Any) -> bool:
    """Compare a field value against a query value, tolerant of Enum wrapping and string case.

    Enum-valued fields (e.g. ``Bill.type``) previously compared directly against
    plain-string query values, so ``filter(type="hr")`` silently matched nothing
    when the stored value was ``LegislationType.HR`` (case- or wrapper-sensitive).
    """
    left = _comparable_value(item_value)
    right = _comparable_value(query_value)
    if isinstance(left, str) and isinstance(right, str):
        return left.lower() == right.lower()
    return left == right


@dataclass
class FieldMapping:
    """Per-field shorthand-query config: either ``enum_class=StateCode`` or a
    custom ``expand_value=lambda v: [v, v.upper()]``."""

    expand_value: Callable[[Any], list[Any]] | None = None
    enum_class: Type[Enum] | None = None

    def get_expander(self) -> Callable[[Any], list[Any]] | None:
        """Return the configured expander, preferring `expand_value` over `enum_class`."""
        if self.expand_value:
            return self.expand_value
        if self.enum_class:
            return enum_expander(self.enum_class)
        return None


@dataclass
class QueryConfig(Generic[ItemT, CollectionT]):
    """Collection class, items field name, and optional validation/mapping settings
    that parameterize a `CollectionQuery` for one entity type."""

    collection_class: type[CollectionT]
    items_field: str
    item_class: type[ItemT] | None = None
    field_mappings: dict[str, FieldMapping] | None = None
    validate_fields: bool = True


class CollectionQuery(Generic[ItemT, CollectionT]):
    """Filter/sort/paginate a list of items, eagerly or lazily (chained).

    Example: ``query.filter(state="CA", lazy=True).order_by("name").execute()``.
    """

    def __init__(
        self,
        items: list[ItemT],
        config: QueryConfig[ItemT, CollectionT]
    ):
        self._items = items
        self._config = config
        self._valid_fields: set[str] | None = None

    def _get_valid_fields(self) -> set[str]:
        """Field names valid for the configured item class, cached after the first call."""
        if self._valid_fields is not None:
            return self._valid_fields

        if not self._config.validate_fields or not self._config.item_class:
            self._valid_fields = set()
            return self._valid_fields

        item_class = self._config.item_class
        fields = set()

        if hasattr(item_class, 'model_fields'):  # Pydantic v2
            fields = set(item_class.model_fields.keys())
        elif hasattr(item_class, '__fields__'):  # Pydantic v1
            fields = set(item_class.__fields__.keys())
        elif hasattr(item_class, '__annotations__'):  # plain classes
            fields = set(item_class.__annotations__.keys())

        self._valid_fields = fields
        return fields

    def _validate_field(self, field: str) -> None:
        """Raise ValueError (with a fuzzy-matched suggestion) if `field` isn't a real attribute."""
        if not self._config.validate_fields or not self._config.item_class:
            return

        valid_fields = self._get_valid_fields()
        if not valid_fields:
            return

        if field not in valid_fields:
            item_class_name = self._config.item_class.__name__
            suggestions = get_close_matches(field, valid_fields, n=3, cutoff=0.6)
            error_msg = f"Invalid field '{field}' for {item_class_name}."

            if suggestions:
                error_msg += "\n\nDid you mean one of these?\n"
                for suggestion in suggestions:
                    error_msg += f"  - {suggestion}\n"
            else:
                sorted_fields = sorted(valid_fields)
                error_msg += "\n\nAvailable fields:\n"
                for valid_field in sorted_fields[:10]:
                    error_msg += f"  - {valid_field}\n"
                if len(sorted_fields) > 10:
                    error_msg += f"  ... and {len(sorted_fields) - 10} more"

            raise ValueError(error_msg)
    
    def filter(
        self,
        lazy: bool = False,
        **kwargs
    ) -> CollectionT | CollectionQuery[ItemT, CollectionT]:
        """Filter items by field values (e.g. state="CA" also matches "California"
        when a field mapping is configured). Pass lazy=True to keep chaining."""
        if not isinstance(lazy, bool):
            raise TypeError(
                f"filter() 'lazy' parameter must be a boolean, got {type(lazy).__name__}. "
                f"If you're trying to pass a lambda or function, use .where() instead: "
                f"collection.query().where(lambda x: ...)"
            )

        # A common mistake: calling filter(lambda x: ...) as if it were Python's builtin filter().
        if kwargs and any(callable(v) for v in list(kwargs.values())[:1]):
            raise TypeError(
                "filter() does not accept callable/lambda values. "
                "Use .where() for predicate-based filtering: "
                "collection.query().where(lambda item: ...)"
            )

        for field in kwargs.keys():
            self._validate_field(field)

        filtered = [
            item for item in self._items
            if all(self._field_matches(item, k, v) for k, v in kwargs.items())
        ]
        new_query = CollectionQuery(filtered, self._config)
        return new_query if lazy else new_query.execute()

    def _field_matches(self, item: ItemT, field: str, query_value: Any) -> bool:
        """Compare an item's field against a query value, expanding via the
        field's mapping (if any) before falling back to plain equality."""
        item_value = getattr(item, field, None)

        if self._config.field_mappings and field in self._config.field_mappings:
            mapping = self._config.field_mappings[field]
            expander = mapping.get_expander()
            if expander:
                possible_values = expander(query_value)  # e.g. "CA" -> ["CA", "California"]
                return any(_values_match(item_value, possible) for possible in possible_values)

        return _values_match(item_value, query_value)
    
    def where(
        self,
        predicate: Callable[[ItemT], bool],
        lazy: bool = False
    ) -> CollectionT | CollectionQuery[ItemT, CollectionT]:
        """Filter items with a predicate function, e.g. ``where(lambda x: x.year > 2020)``."""
        if not callable(predicate):
            raise TypeError(
                f"where() expects a callable predicate function, got {type(predicate).__name__}. "
                f"Usage: collection.query().where(lambda item: item.field == value)"
            )

        if not isinstance(lazy, bool):
            raise TypeError(
                f"where() 'lazy' parameter must be a boolean, got {type(lazy).__name__}"
            )

        try:
            filtered = [item for item in self._items if predicate(item)]
        except AttributeError as e:
            raise AttributeError(
                f"Error in where() predicate: {e}\n"
                f"Make sure the field exists on the item. "
                f"Available fields can be checked with validation enabled."
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Error executing where() predicate: {e}\n"
                f"Predicate: {predicate}"
            ) from e

        new_query = CollectionQuery(filtered, self._config)
        return new_query if lazy else new_query.execute()

    def order_by(
        self,
        field: str,
        reverse: bool = False,
        lazy: bool = False
    ) -> CollectionT | CollectionQuery[ItemT, CollectionT]:
        """Sort items by a field name, ascending unless reverse=True."""
        self._validate_field(field)

        # None sorts first without discarding legitimate falsy sort keys
        # (0, False, "") the way `getattr(...) or ""` would.
        def _sort_key(item: ItemT) -> tuple[int, Any]:
            value = getattr(item, field, None)
            return (0, "") if value is None else (1, value)

        sorted_items = sorted(
            self._items,
            key=_sort_key,
            reverse=reverse
        )
        new_query = CollectionQuery(sorted_items, self._config)
        return new_query if lazy else new_query.execute()

    def limit(
        self,
        n: int,
        lazy: bool = False
    ) -> CollectionT | CollectionQuery[ItemT, CollectionT]:
        """Keep only the first n items."""
        new_query = CollectionQuery(self._items[:n], self._config)
        return new_query if lazy else new_query.execute()

    def skip(
        self,
        n: int,
        lazy: bool = False
    ) -> CollectionT | CollectionQuery[ItemT, CollectionT]:
        """Drop the first n items."""
        new_query = CollectionQuery(self._items[n:], self._config)
        return new_query if lazy else new_query.execute()

    def execute(self) -> CollectionT:
        """Materialize the current items into a collection instance."""
        kwargs = {self._config.items_field: self._items}
        return self._config.collection_class(**kwargs)
    
    def first(self) -> ItemT | None:
        """Get the first item, or None if empty."""
        return self._items[0] if self._items else None
    
    def last(self) -> ItemT | None:
        """Get the last item, or None if empty."""
        return self._items[-1] if self._items else None
    
    def count(self) -> int:
        """Count the number of items."""
        return len(self._items)
    
    def exists(self) -> bool:
        """Check if any items exist."""
        return len(self._items) > 0
    
    def to_list(self) -> list[ItemT]:
        """Return the current item list (canonical alternative to iterating the collection)."""
        return self._items
    
    def group_by(self, field: str) -> dict[Any, CollectionT]:
        """Group items into a dict keyed by field value, e.g. ``{"CA": Members(...), ...}``."""
        self._validate_field(field)

        groups: dict[Any, list[ItemT]] = {}
        for item in self._items:
            key = getattr(item, field, None)
            groups.setdefault(key, []).append(item)
        
        # Convert each group to a collection instance
        result = {}
        for key, items in groups.items():
            kwargs = {self._config.items_field: items}
            result[key] = self._config.collection_class(**kwargs)
        
        return result
    
    # Python protocols
    def __iter__(self) -> Iterator[ItemT]:
        """Allow iteration over items."""
        return iter(self._items)
    
    def __len__(self) -> int:
        """Support len() function."""
        return len(self._items)
    
    def __getitem__(self, key: int | slice) -> ItemT | CollectionT:
        """Support indexing and slicing."""
        result = self._items[key]
        if isinstance(key, slice):
            kwargs = {self._config.items_field: result}
            return self._config.collection_class(**kwargs)
        return result
    
    def __bool__(self) -> bool:
        """Support truthiness checks."""
        return bool(self._items)
    
    def __repr__(self) -> str:
        """String representation."""
        class_name = self._config.collection_class.__name__
        return f"<{class_name}Query: {len(self._items)} items>"


def create_query_builder(
    collection_class: type[CollectionT],
    items_field: str,
    item_class: type[Any] | None = None,
    field_mappings: dict[str, FieldMapping] | None = None,
    validate_fields: bool = True
) -> type[CollectionQuery[Any, CollectionT]]:
    """Build a `CollectionQuery` subclass pre-bound to one collection/item class pair.

    Example::

        MembersQuery = create_query_builder(
            collection_class=Members,
            items_field="members",
            item_class=Member,
            field_mappings={"state": FieldMapping(enum_class=StateCode)},
        )
        query.filter(state="CA")   # matches "California" too, via the mapping
        query.filter(stte="CA")    # raises ValueError with a "did you mean" suggestion
    """
    config = QueryConfig(
        collection_class=collection_class,
        items_field=items_field,
        item_class=item_class,
        field_mappings=field_mappings,
        validate_fields=validate_fields
    )

    class ConfiguredQuery(CollectionQuery[Any, CollectionT]):
        def __init__(self, items: list[Any]):
            super().__init__(items, config)

    # Give the dynamically created class a readable name for debugging/repr.
    ConfiguredQuery.__name__ = f"{collection_class.__name__}Query"
    ConfiguredQuery.__qualname__ = f"{collection_class.__name__}Query"

    return ConfiguredQuery
