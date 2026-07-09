"""
Generic Query Builder for Collection Models

Provides a reusable query builder pattern that can be applied to any
collection model (Members, Bills, Committees, etc.).

Features:
- Generic implementation works for all collection types
- Enum-based field mappings for shorthand queries (e.g., "CA" -> "California")
- Eager/lazy evaluation modes
- Full Python protocol support
- Field validation to catch typos and invalid attributes

This eliminates the need to create custom query classes for each model.
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
    """
    Create a value expander function from an Enum class.
    
    Automatically handles lookups in both directions:
    - Code -> Value: "CA" -> "California"
    - Value -> Code: "California" -> "CA"
    
    Args:
        enum_class: The Enum class (e.g., StateCode, LegislationType)
    
    Returns:
        Function that expands query values to include all matching forms
    
    Examples:
        from congressgov.models.base.enums import StateCode
        
        expander = enum_expander(StateCode)
        expander("CA")          # ["CA", "California"]
        expander("California")  # ["California", "CA"]
    """
    # NOTE: Build lookup dicts for O(1) access
    code_to_value = {member.name: member.value for member in enum_class}
    value_to_code = {member.value.lower(): member.name for member in enum_class}
    
    def expander(query_value: Any) -> list[Any]:
        """Expand query value to include both code and full value."""
        # NOTE: Only process strings
        if not isinstance(query_value, str):
            return [query_value]
        
        values = [query_value]
        upper_query = query_value.upper()
        lower_query = query_value.lower()
        
        # NOTE: Forward lookup (code -> value)
        # Example: "CA" -> "California"
        if upper_query in code_to_value:
            values.append(code_to_value[upper_query])
        
        # NOTE: Reverse lookup (value -> code)  
        # Example: "California" -> "CA"
        if lower_query in value_to_code:
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
    """
    Configuration for field-specific query behavior.
    
    Enables shorthand queries by expanding values to multiple possible matches.
    
    Attributes:
        expand_value: Custom function to expand query values
        enum_class: Enum class for automatic code/value expansion
    
    Examples:
        # Using enum (recommended)
        FieldMapping(enum_class=StateCode)
        
        # Using custom function
        FieldMapping(expand_value=lambda v: [v, v.upper()])
    """
    expand_value: Callable[[Any], list[Any]] | None = None
    enum_class: Type[Enum] | None = None
    
    def get_expander(self) -> Callable[[Any], list[Any]] | None:
        """
        Get the expander function.
        
        NOTE: If both expand_value and enum_class are set, expand_value takes precedence.
        NOTE: If enum_class is set, creates expander automatically.
        
        Returns:
            Expander function or None
        """
        if self.expand_value:
            return self.expand_value
        if self.enum_class:
            return enum_expander(self.enum_class)
        return None


@dataclass
class QueryConfig(Generic[ItemT, CollectionT]):
    """
    Configuration for creating a query builder instance.
    
    Attributes:
        collection_class: The collection class to instantiate (e.g., Members)
        items_field: Name of the field containing items (e.g., "members", "bills")
        item_class: Optional item class for field validation (e.g., Member, Bill)
        field_mappings: Optional mappings for shorthand query support
        validate_fields: Whether to validate field names (default: True)
    
    Examples:
        # Basic config
        QueryConfig(collection_class=Members, items_field="members")
        
        # With field mappings for shorthand
        QueryConfig(
            collection_class=Members,
            items_field="members",
            item_class=Member,
            field_mappings={"state": FieldMapping(enum_class=StateCode)}
        )
    """
    collection_class: type[CollectionT]
    items_field: str
    item_class: type[ItemT] | None = None
    field_mappings: dict[str, FieldMapping] | None = None
    validate_fields: bool = True


class CollectionQuery(Generic[ItemT, CollectionT]):
    """
    Generic query builder for collection models.
    
    Supports filtering, sorting, pagination, and more with both
    eager and lazy evaluation modes.
    
    Type Parameters:
        ItemT: Type of individual items (Member, Bill, etc.)
        CollectionT: Type of collection class (Members, Bills, etc.)
    
    Args:
        items: List of items to query
        config: Query configuration specifying collection class and field names
    
    Examples:
        # Create query builder for Members
        config = QueryConfig(collection_class=Members, items_field="members")
        query = CollectionQuery(members_list, config)
        
        # Use it
        filtered = query.filter(state="CA", lazy=True).execute()
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
        """
        Get valid field names from the item class.
        
        NOTE: Caches result after first call for performance.
        NOTE: Works with Pydantic models (model_fields) and regular classes (__annotations__).
        
        Returns:
            Set of valid field names, or empty set if validation is disabled
        """
        # NOTE: Return cached result if available
        if self._valid_fields is not None:
            return self._valid_fields
        
        # NOTE: If validation is disabled or no item class, return empty set (no validation)
        if not self._config.validate_fields or not self._config.item_class:
            self._valid_fields = set()
            return self._valid_fields
        
        item_class = self._config.item_class
        fields = set()
        
        # NOTE: Try Pydantic v2 first (model_fields)
        if hasattr(item_class, 'model_fields'):
            fields = set(item_class.model_fields.keys())
        # NOTE: Try Pydantic v1 (fields)
        elif hasattr(item_class, '__fields__'):
            fields = set(item_class.__fields__.keys())
        # NOTE: Fall back to annotations for regular classes
        elif hasattr(item_class, '__annotations__'):
            fields = set(item_class.__annotations__.keys())
        
        # NOTE: Cache for future calls
        self._valid_fields = fields
        return fields
    
    def _validate_field(self, field: str) -> None:
        """
        Validate that a field name is valid for the item class.
        
        NOTE: Raises ValueError with helpful message if field is invalid.
        NOTE: Suggests similar field names using fuzzy matching.
        
        Args:
            field: Field name to validate
        
        Raises:
            ValueError: If field is invalid (when validation is enabled)
        """
        # NOTE: Skip validation if disabled or no item class
        if not self._config.validate_fields or not self._config.item_class:
            return
        
        valid_fields = self._get_valid_fields()
        
        # NOTE: Skip validation if we couldn't determine valid fields
        if not valid_fields:
            return
        
        # NOTE: Check if field is valid
        if field not in valid_fields:
            item_class_name = self._config.item_class.__name__
            
            # NOTE: Use fuzzy matching to suggest corrections
            suggestions = get_close_matches(field, valid_fields, n=3, cutoff=0.6)
            
            error_msg = f"Invalid field '{field}' for {item_class_name}."
            
            if suggestions:
                error_msg += "\n\nDid you mean one of these?\n"
                for suggestion in suggestions:
                    error_msg += f"  - {suggestion}\n"
            else:
                # NOTE: Show available fields if no close matches
                sorted_fields = sorted(valid_fields)
                error_msg += "\n\nAvailable fields:\n"
                for valid_field in sorted_fields[:10]:  # Show first 10
                    error_msg += f"  - {valid_field}\n"
                if len(sorted_fields) > 10:
                    error_msg += f"  ... and {len(sorted_fields) - 10} more"
            
            raise ValueError(error_msg)
    
    def filter(
        self,
        lazy: bool = False,
        **kwargs
    ) -> CollectionT | CollectionQuery[ItemT, CollectionT]:
        """
        Filter items by field values.
        
        Supports shorthand queries via field mappings (e.g., state="CA" matches "California").
        
        Args:
            lazy: If True, return query builder. If False, return collection.
            **kwargs: Field-value pairs to filter by.
        
        Examples:
            # Eager (with shorthand via enum mapping)
            result = query.filter(state="CA")  # Matches "California"
            
            # Lazy
            result = query.filter(state="CA", lazy=True).order_by("name").execute()
        
        Raises:
            TypeError: If lazy parameter is not a boolean or if a callable is passed
            ValueError: If any field name is invalid (when validation is enabled)
        """
        # NOTE: Type safety - validate lazy parameter
        if not isinstance(lazy, bool):
            raise TypeError(
                f"filter() 'lazy' parameter must be a boolean, got {type(lazy).__name__}. "
                f"If you're trying to pass a lambda or function, use .where() instead:\n"
                f"  ❌ collection.filter(lambda x: ...)\n"
                f"  ✅ collection.query().where(lambda x: ...)"
            )
        
        # NOTE: Common mistake - check if user passed a callable as first positional arg
        # This can happen if they call filter(lambda x: ...) thinking it's like Python's filter()
        if kwargs and any(callable(v) for v in list(kwargs.values())[:1]):
            first_key = list(kwargs.keys())[0]
            raise TypeError(
                f"filter() does not accept callable/lambda functions. "
                f"Use .where() for predicate-based filtering:\n"
                f"  ❌ collection.filter({first_key}=<function>)\n"
                f"  ✅ collection.query().where(lambda item: ...)"
            )
        
        # NOTE: Validate all field names before filtering
        for field in kwargs.keys():
            self._validate_field(field)
        
        # NOTE: Use _field_matches for shorthand support
        filtered = [
            item for item in self._items
            if all(self._field_matches(item, k, v) for k, v in kwargs.items())
        ]
        new_query = CollectionQuery(filtered, self._config)
        return new_query if lazy else new_query.execute()
    
    def _field_matches(self, item: ItemT, field: str, query_value: Any) -> bool:
        """
        Check if an item's field value matches the query value.
        
        NOTE: Supports enum-based field mappings for shorthand queries.
        NOTE: Falls back to standard equality if no mapping exists.
        
        Args:
            item: The item to check
            field: Field name to check
            query_value: Value to match against
        
        Returns:
            True if field matches, False otherwise
        """
        item_value = getattr(item, field, None)
        
        # NOTE: Check for field mapping configuration
        if self._config.field_mappings and field in self._config.field_mappings:
            mapping = self._config.field_mappings[field]
            expander = mapping.get_expander()
            
            if expander:
                # NOTE: Expand query value to all possible matching values
                # Example: "CA" -> ["CA", "California"]
                possible_values = expander(query_value)
                return any(_values_match(item_value, possible) for possible in possible_values)
        
        # NOTE: Equality check tolerant of Enum wrapping / string case (no mapping)
        return _values_match(item_value, query_value)
    
    def where(
        self,
        predicate: Callable[[ItemT], bool],
        lazy: bool = False
    ) -> CollectionT | CollectionQuery[ItemT, CollectionT]:
        """
        Filter items using a custom predicate function.
        
        Args:
            predicate: Function that takes an item and returns bool
            lazy: If True, return query builder. If False, return collection.
        
        Examples:
            # Eager
            result = query.where(lambda x: x.year > 2020)
            
            # Lazy
            result = query.where(lambda x: x.year > 2020, lazy=True).limit(10).execute()
        
        Raises:
            TypeError: If predicate is not callable or lazy is not a boolean
        """
        # NOTE: Type safety - validate predicate parameter
        if not callable(predicate):
            raise TypeError(
                f"where() expects a callable predicate function, got {type(predicate).__name__}. "
                f"Usage: collection.query().where(lambda item: item.field == value)"
            )
        
        # NOTE: Type safety - validate lazy parameter
        if not isinstance(lazy, bool):
            raise TypeError(
                f"where() 'lazy' parameter must be a boolean, got {type(lazy).__name__}"
            )
        
        # NOTE: Execute predicate with error handling
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
        """
        Sort items by a field.
        
        Args:
            field: Field name to sort by
            reverse: If True, sort descending
            lazy: If True, return query builder. If False, return collection.
        
        Raises:
            ValueError: If field name is invalid (when validation is enabled)
        """
        # NOTE: Validate field name before sorting
        self._validate_field(field)
        
        # NOTE: Sort key must treat None as the "smallest" value without discarding
        # legitimate falsy sort keys (0, False, "") the way `getattr(...) or ""` did.
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
        """
        Limit to first n items.
        
        Args:
            n: Maximum number of items
            lazy: If True, return query builder. If False, return collection.
        """
        new_query = CollectionQuery(self._items[:n], self._config)
        return new_query if lazy else new_query.execute()
    
    def skip(
        self,
        n: int,
        lazy: bool = False
    ) -> CollectionT | CollectionQuery[ItemT, CollectionT]:
        """
        Skip first n items.
        
        Args:
            n: Number of items to skip
            lazy: If True, return query builder. If False, return collection.
        """
        new_query = CollectionQuery(self._items[n:], self._config)
        return new_query if lazy else new_query.execute()
    
    def execute(self) -> CollectionT:
        """
        Execute the query and return a collection instance.
        
        Returns:
            Collection instance with filtered/sorted items
        
        Example:
            members = query.filter(state="CA", lazy=True).execute()
        """
        # Create collection instance with items
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
        """
        Group items by field value.
        
        Args:
            field: Field name to group by
        
        Returns:
            Dictionary mapping field values to collection instances
        
        Example:
            by_state = query.group_by("state")
            # Returns: {"CA": Members(...), "NY": Members(...)}
        
        Raises:
            ValueError: If field name is invalid (when validation is enabled)
        """
        # NOTE: Validate field name before grouping
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
    """
    Factory function to create a configured query builder class.
    
    Creates a query builder with pre-configured collection class, items field,
    optional field mappings for shorthand query support, and field validation.
    
    Args:
        collection_class: The collection class (e.g., Members)
        items_field: Name of the items field (e.g., "members")
        item_class: Optional item class for field validation (e.g., Member)
        field_mappings: Optional field mappings for shorthand support
        validate_fields: Whether to validate field names (default: True)
    
    Returns:
        A configured CollectionQuery class
    
    Examples:
        # Basic query builder
        MembersQuery = create_query_builder(Members, "members")
        
        # With validation and enum-based shorthand support
        from congressgov.models.base.enums import StateCode
        from congressgov.models.entities.member import Member
        
        MembersQuery = create_query_builder(
            collection_class=Members,
            items_field="members",
            item_class=Member,
            field_mappings={
                "state": FieldMapping(enum_class=StateCode)
            }
        )
        
        # Now "CA" automatically matches "California" and invalid fields are caught
        ca_members = query.filter(state="CA")  # ✓ Works
        bad_query = query.filter(stte="CA")    # ✗ Raises ValueError with suggestion
    """
    # NOTE: Create config with field mappings and validation settings
    config = QueryConfig(
        collection_class=collection_class,
        items_field=items_field,
        item_class=item_class,
        field_mappings=field_mappings,
        validate_fields=validate_fields
    )
    
    class ConfiguredQuery(CollectionQuery[Any, CollectionT]):
        """Pre-configured query builder with field mapping and validation support."""
        
        def __init__(self, items: list[Any]):
            super().__init__(items, config)
    
    # NOTE: Set a better name for the class for debugging/repr
    ConfiguredQuery.__name__ = f"{collection_class.__name__}Query"
    ConfiguredQuery.__qualname__ = f"{collection_class.__name__}Query"
    
    return ConfiguredQuery
