from __future__ import annotations
from typing import Optional, Generic, TypeVar, Any, get_args, get_origin, Union
from copy import deepcopy
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, model_validator, field_serializer
from pydantic.alias_generators import to_camel

"""
ENHANCED MODEL CLASS WITH UNIFIED FIELD PROCESSING

This Model class provides unified field processing capabilities including automatic
container extraction, auto-wrapping, auto-unwrapping, and Union type processing.

FEATURES:
    1. Container extraction: Automatically extracts data from container structures
    2. Auto-wrapping: Wraps lists in expected container structures
    3. Auto-unwrapping: Unwraps formats arrays and item-wrapped fields
    4. Union type processing: Handles Union types with container classes
    5. Type resolution: Resolves string-based type hints to actual types
    6. Debug logging: Centralized debug logging for troubleshooting
"""


class Model(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra='allow',      # HACK: May create issues - consider changing
        frozen=False,
        validate_default=True,
        use_enum_values=True
    )

    # Runtime-only attrs (not API payload); omit from __repr__ to avoid cycles/noise.
    _REPR_SKIP_ATTRS = frozenset({"client", "_parent_collection", "_parent_entity"})

    @model_validator(mode="before")
    @classmethod
    def _parse_datetime_fields(cls, values: Any) -> Any:
        """
        === [DATETIME/DATE STRING PARSING] ===
        Automatically converts string representations of datetime and date fields
        to their proper Python types before validation.
        
        Supports the following formats:
        - ISO 8601: YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS.ffffffZ
        - Date only: YYYY-MM-DD
        
        NOTE: This validator runs before Pydantic's validation, ensuring that
        datetime/date strings are properly converted to Python datetime/date objects.
        """
        if not isinstance(values, dict):
            return values
        
        # Get the model's field annotations to determine which fields are datetime/date
        if not hasattr(cls, '__annotations__'):
            return values
        
        # Process each field that's annotated as datetime or date
        for field_name, field_type in cls.__annotations__.items():
            # Extract the actual type from Optional, Union, etc.
            actual_types = cls._extract_types(field_type)
            
            # Check if datetime or date is in the actual types
            if not (datetime in actual_types or date in actual_types):
                continue
            
            # Check both the field name and its camelCase alias
            field_value = None
            key_used = None
            
            # Try the original field name
            if field_name in values:
                field_value = values[field_name]
                key_used = field_name
            else:
                # Try the camelCase alias
                camel_name = to_camel(field_name)
                if camel_name in values:
                    field_value = values[camel_name]
                    key_used = camel_name
            
            # If we found a value and it's a string, parse it
            if key_used and isinstance(field_value, str):
                try:
                    if datetime in actual_types:
                        # Parse as datetime
                        # Handle both with and without timezone suffix
                        parsed = cls._parse_datetime_string(field_value)
                        values[key_used] = parsed
                    elif date in actual_types:
                        # Parse as date
                        parsed = cls._parse_date_string(field_value)
                        values[key_used] = parsed
                except (ValueError, AttributeError):
                    # If parsing fails, leave it as-is and let Pydantic handle the error
                    pass
        
        return values
    
    @staticmethod
    def _extract_types(field_type: Any) -> set:
        """
        === [TYPE EXTRACTION HELPER] ===
        Extracts all actual types from a type annotation, handling:
        - Optional[T] (which is Union[T, None])
        - Union[T1, T2, ...]
        - Direct types like datetime, date, str, etc.
        
        Returns:
            set: A set of all actual types found in the annotation
        """
        types = set()
        origin = get_origin(field_type)
        
        # Handle Union and Optional (Optional[T] is Union[T, None])
        if origin is Union:
            for arg in get_args(field_type):
                if arg is not type(None):  # Skip None
                    types.add(arg)
        # Handle direct type annotations
        elif field_type is not None and field_type is not type(None):
            types.add(field_type)
        
        return types
    
    @staticmethod
    def _parse_datetime_string(value: str) -> datetime:
        """
        === [DATETIME STRING PARSER] ===
        Parses datetime strings in ISO 8601 format.
        
        Handles:
        - YYYY-MM-DDTHH:MM:SSZ
        - YYYY-MM-DDTHH:MM:SS.ffffffZ
        - YYYY-MM-DDTHH:MM:SS
        - YYYY-MM-DD (assumes midnight)
        
        NOTE: The 'Z' suffix indicates UTC time and is properly handled.
        """
        # Remove 'Z' suffix if present (indicates UTC)
        if value.endswith('Z'):
            value = value[:-1]
        
        # Try parsing with microseconds
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            # Try with just date (will add time as 00:00:00)
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                # Last resort: try strptime with common format
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    
    @staticmethod
    def _parse_date_string(value: str) -> date:
        """
        === [DATE STRING PARSER] ===
        Parses date strings in ISO 8601 format (YYYY-MM-DD).
        
        NOTE: If a full datetime string is provided, extracts just the date portion.
        """
        # If it's a datetime string, extract just the date part
        if 'T' in value:
            value = value.split('T')[0]
        
        return date.fromisoformat(value)

    def pretty_print(self, indent: int = 0, max_width: int = 120) -> str:
        """
        Pretty print the model and its nested fields in a readable, indented format.
        Handles nested models, lists, dicts, and basic types.
        """
        from collections.abc import Mapping, Sequence

        def _is_model(obj):
            # Accepts both pydantic BaseModel and our Model
            return hasattr(obj, "__fields__") or hasattr(obj, "model_fields")

        def _pretty(obj, level):
            pad = "    " * level
            if _is_model(obj):
                cls_name = obj.__class__.__name__
                items = []
                # Use model_fields for pydantic v2, __fields__ for v1
                fields = getattr(obj, "model_fields", None) or getattr(obj, "__fields__", None)
                if fields is None:
                    # fallback: dir(obj)
                    fields = {k: None for k in dir(obj) if not k.startswith("_")}
                for k in fields:
                    v = getattr(obj, k, None)
                    if v is not None:
                        pretty_v = _pretty(v, level + 1)
                        items.append(f"{pad}    {k}={pretty_v}")
                if not items:
                    return f"{cls_name}()"
                return f"{cls_name}(\n" + ",\n".join(items) + f"\n{pad})"
            elif isinstance(obj, Mapping):
                if not obj:
                    return "{}"
                items = []
                for k, v in obj.items():
                    pretty_v = _pretty(v, level + 1)
                    items.append(f"{pad}    {repr(k)}: {pretty_v}")
                return "{\n" + ",\n".join(items) + f"\n{pad}}}"
            elif isinstance(obj, str):
                # Show long strings as triple-quoted if they contain newlines
                if "\n" in obj:
                    return f'"""{obj}"""'
                return repr(obj)
            elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
                if not obj:
                    return "[]"
                items = [_pretty(v, level + 1) for v in obj]
                return "[\n" + ",\n".join(f"{pad}    {item}" for item in items) + f"\n{pad}]"
            elif isinstance(obj, (datetime, )):
                return repr(obj)
            else:
                return repr(obj)

        return _pretty(self, indent)

    @field_serializer('*', when_used='json')
    def serialize_datetime(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return value

    def __repr__(self):
        attrs = []
        model_fields = type(self).model_fields
        for name in model_fields:
            if name in self._REPR_SKIP_ATTRS:
                continue
            value = getattr(self, name, None)
            if value is not None:
                attrs.append(f"{name}={value!r}")
        extra = getattr(self, "__pydantic_extra__", None) or {}
        for name, value in extra.items():
            if name in self._REPR_SKIP_ATTRS or name.startswith("_"):
                continue
            if value is not None:
                attrs.append(f"{name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    @classmethod
    def get_aliases(model_cls):
        return {
            name: (field.alias if hasattr(field, "alias") and field.alias else name)
            for name, field in model_cls.model_fields.items()
        }

    @classmethod
    def model_validate(cls, obj, debug: bool = False, **kwargs):
        """
        Debug-enabled model_validate: outputs comprehensive debugging statements
        only if debug=True, then calls BaseModel.model_validate to perform actual validation.
        If validation fails or all attributes are None, tries unwrapping single top-level key.
        """
        if debug:
            aliases = cls.get_aliases()
            print(f"[DEBUG][model_validate] Aliases: {aliases}")
            print(f"[DEBUG][model_validate] Called for {cls.__name__}")
            print(f"[DEBUG][model_validate] Input object type: {type(obj)}")
            print(f"[DEBUG][model_validate] Input object value: {repr(obj)}")
            if isinstance(obj, dict):
                print(f"[DEBUG][model_validate] Input dict keys: {list(obj.keys())}")
            if hasattr(cls, '__annotations__'):
                print(f"[DEBUG][model_validate] Class annotations: {cls.__annotations__}")
            else:
                print(f"[DEBUG][model_validate] No __annotations__ found for {cls.__name__}")
            if hasattr(cls, 'model_config'):
                print(f"[DEBUG][model_validate] model_config: {getattr(cls, 'model_config', None)}")
            else:
                print(f"[DEBUG][model_validate] No model_config found for {cls.__name__}")

            # Print per-field input values if possible
            if isinstance(obj, dict) and hasattr(cls, '__annotations__'):
                print(f"[DEBUG][model_validate] Per-field input values for {cls.__name__}:")
                for field in cls.__annotations__:
                    value = obj.get(field, None)
                    print(f"    [DEBUG][model_validate][field] {field}: {repr(value)}")
            elif hasattr(obj, '__dict__') and hasattr(cls, '__annotations__'):
                print(f"[DEBUG][model_validate] Per-field input values for {cls.__name__} (from __dict__):")
                for field in cls.__annotations__:
                    value = getattr(obj, field, None)
                    print(f"    [DEBUG][model_validate][field] {field}: {repr(value)}")
            else:
                print(f"[DEBUG][model_validate] Unable to print per-field input values for {cls.__name__}")

        try:
            # Call BaseModel's model_validate to perform actual validation
            result = super().model_validate.__func__(cls, obj, **kwargs)

            # Check if all attributes are None
            if hasattr(result, '__dict__'):
                all_none = all(v is None for v in result.__dict__.values())
                if all_none:
                    if debug:
                        print(f"[DEBUG][model_validate] All attributes are None for {cls.__name__}, trying unwrapping")
                    # Try unwrapping single top-level key
                    if isinstance(obj, dict) and len(obj) == 1:
                        single_key = next(iter(obj))
                        single_value = obj[single_key]
                        if debug:
                            print(f"[DEBUG][model_validate] Trying to unwrap single key '{single_key}' with value: {repr(single_value)}")
                        return super().model_validate.__func__(cls, single_value, **kwargs)

            return result

        except Exception as e:
            if debug:
                print(f"[DEBUG][model_validate] Validation failed for {cls.__name__}: {e}")

            # If validation fails and obj is a dict with single key, try unwrapping
            if isinstance(obj, dict) and len(obj) == 1:
                single_key = next(iter(obj))
                single_value = obj[single_key]
                if debug:
                    print(f"[DEBUG][model_validate] Trying to unwrap single key '{single_key}' with value: {repr(single_value)}")
                try:
                    return super().model_validate.__func__(cls, single_value, **kwargs)
                except Exception as unwrap_e:
                    if debug:
                        print(f"[DEBUG][model_validate] Unwrapping also failed: {unwrap_e}")
                    raise e  # Re-raise original exception

            raise
    

T = TypeVar('T')


class Pagination(Model):
    count: int
    next_url: Optional[str] = None
    previous_url: Optional[str] = None


class ApiEnvelope(Model, Generic[T]):
    """
    === [API ENVELOPE MODEL] ===
    This class wraps API responses, extracting the main data payload and supporting optional pagination/request info.
    Data validation is intentionally minimal and only processes the envelope structure as in _traverse_keys.
    """

    data: T | None = None              # The main data payload, now typed as T
    data_key: str | None = None        # The top-level key for the data payload
    pagination: Pagination | None = None
    request: dict | None = None

    # === [ALLOW EXTRA FIELDS] ===
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    def _traverse_keys(
        cls, 
        values: dict[str, Any], 
        debug_check_dict: bool = False
    ) -> dict[str, Any]:
        """
        === [ENVELOPE UNWRAPPING LOGIC] ===
        This validator only unwraps the envelope to extract the main data payload.
        No additional validation or coercion is performed.
        Also sets the data_key attribute to the top-level key used for the data payload.

        The dict check can be disabled for debugging purposes by setting debug_check_dict=False.
        """
        if debug_check_dict:
            print("\n[DEBUG] ApiEnvelope._traverse_keys called")
            print(f"  [DEBUG] Input values keys: {list(values.keys()) if isinstance(values, dict) else 'Not a dict'}")

        values = deepcopy(values)
        # If debug_check_dict is False, always assume values is a dict (original behavior)
        if not debug_check_dict:
            # Remove 'request' and 'pagination' keys to find the main data key(s)
            new_keys = {k: v for k, v in values.items() if k not in ('request', 'pagination')}
            # No debug print here, as debug_check_dict is False
            if len(new_keys) == 1:
                only_key = next(iter(new_keys))
                if isinstance(new_keys[only_key], dict):
                    values['data'] = new_keys[only_key]
                else:
                    values['data'] = {only_key: new_keys[only_key]}
                values['data_key'] = only_key
            else:
                values['data'] = new_keys
                values['data_key'] = None
            return values
        # If debug_check_dict is True, only proceed if values is a dict
        elif isinstance(values, dict):
            new_keys = {k: v for k, v in values.items() if k not in ('request', 'pagination')}
            if debug_check_dict:
                print(f"  [DEBUG] New keys after removing request/pagination: {list(new_keys.keys())}")
            if len(new_keys) == 1:
                only_key = next(iter(new_keys))
                if debug_check_dict:
                    print(f"  [DEBUG] Only key found: {only_key}")
                    print(f"  [DEBUG] Value type: {type(new_keys[only_key])}")
                if isinstance(new_keys[only_key], dict):
                    values['data'] = new_keys[only_key]
                else:
                    values['data'] = {only_key: new_keys[only_key]}
                values['data_key'] = only_key
            else:
                if debug_check_dict:
                    print(f"  [DEBUG] Multiple keys found: {list(new_keys.keys())}, treating entire response as data")
                values['data'] = new_keys
                values['data_key'] = None
            return values
        return values
