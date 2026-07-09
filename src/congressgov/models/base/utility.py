"""Validation helpers and pretty-printing utilities shared across the models layer."""

from __future__ import annotations

import json
import logging
from typing import Any
from datetime import date, datetime

from ..exceptions import FieldValidationError

logger = logging.getLogger(__name__)

MIN_CONGRESS = 1  # The 1st Congress convened in 1789.

# TODO: update this periodically, or derive it dynamically.
CURRENT_CONGRESS = 119

# Valid chamber values
VALID_CHAMBERS = {"house", "senate"}

# Valid bill types
VALID_BILL_TYPES = {"hr", "s", "hjres", "sjres", "hconres", "sconres", "hres", "sres"}


# ============================================================================
# VALIDATION HELPERS
# ============================================================================


def validate_congress_number(
    congress: int,
    allow_future: bool = False,
    field_name: str = "congress"
) -> int:
    """
    Validate congress number is in valid range.
    
    Congress numbers start at 1 (1789-1791) and increment by 1 for each
    2-year term. This function validates that a congress number is:
    - Greater than or equal to 1
    - Not in the future (unless allow_future=True)
    
    Args:
        congress: Congress number to validate
        allow_future: If True, allow congress numbers beyond current (default: False)
        field_name: Name of field being validated (for error messages)
        
    Returns:
        Validated congress number (unchanged if valid)
        
    Raises:
        FieldValidationError: If congress number is invalid
        
    Example:
        >>> validate_congress_number(118)  # Valid
        118
        >>> validate_congress_number(0)  # Invalid
        FieldValidationError: Congress number must be >= 1
        >>> validate_congress_number(200)  # Future congress
        FieldValidationError: Congress 200 is in the future
    """
    if congress < MIN_CONGRESS:
        logger.error(f"Invalid congress number: {congress} < {MIN_CONGRESS}")
        raise FieldValidationError(
            f"Congress number must be >= {MIN_CONGRESS}, got {congress}",
            field=field_name,
            value=congress,
            constraint=f"congress >= {MIN_CONGRESS}"
        )
    
    if not allow_future and congress > CURRENT_CONGRESS:
        logger.warning(f"Congress {congress} is in the future (current: {CURRENT_CONGRESS})")
        raise FieldValidationError(
            f"Congress {congress} is in the future. Current Congress is {CURRENT_CONGRESS}.",
            field=field_name,
            value=congress,
            constraint=f"congress <= {CURRENT_CONGRESS}"
        )
    
    return congress


def validate_date_range(
    date_value: date,
    allow_future: bool = False,
    field_name: str = "date"
) -> date:
    """
    Validate date is not in future (unless explicitly allowed).
    
    Args:
        date_value: Date to validate
        allow_future: If True, allow future dates (default: False)
        field_name: Name of field being validated (for error messages)
        
    Returns:
        Validated date (unchanged if valid)
        
    Raises:
        FieldValidationError: If date is in the future and allow_future=False
        
    Example:
        >>> from datetime import date
        >>> validate_date_range(date(2020, 1, 1))  # Valid past date
        date(2020, 1, 1)
        >>> validate_date_range(date(2030, 1, 1))  # Future date
        FieldValidationError: Date 2030-01-01 is in the future
    """
    if not allow_future:
        today = date.today()
        if date_value > today:
            logger.warning(f"Date {date_value} is in the future")
            raise FieldValidationError(
                f"Date {date_value} is in the future. Today is {today}.",
                field=field_name,
                value=date_value,
                constraint="date <= today"
            )
    
    return date_value


def validate_chamber(
    chamber: str,
    field_name: str = "chamber"
) -> str:
    """
    Validate chamber value with helpful suggestions.
    
    Args:
        chamber: Chamber value to validate ("house" or "senate")
        field_name: Name of field being validated (for error messages)
        
    Returns:
        Validated chamber value (lowercase)
        
    Raises:
        FieldValidationError: If chamber value is invalid
        
    Example:
        >>> validate_chamber("house")  # Valid
        'house'
        >>> validate_chamber("SENATE")  # Valid (case insensitive)
        'senate'
        >>> validate_chamber("commons")  # Invalid
        FieldValidationError: Invalid chamber 'commons'. Must be 'house' or 'senate'
    """
    chamber_lower = chamber.lower()
    
    if chamber_lower not in VALID_CHAMBERS:
        logger.error(f"Invalid chamber value: {chamber}")
        raise FieldValidationError(
            f"Invalid chamber '{chamber}'. Must be one of: {', '.join(sorted(VALID_CHAMBERS))}",
            field=field_name,
            value=chamber,
            allowed_values=list(VALID_CHAMBERS)
        )
    
    return chamber_lower


def validate_bill_type(
    bill_type: str,
    field_name: str = "bill_type"
) -> str:
    """
    Validate bill type with helpful suggestions.
    
    Valid bill types:
    - hr: House Bill
    - s: Senate Bill
    - hjres: House Joint Resolution
    - sjres: Senate Joint Resolution
    - hconres: House Concurrent Resolution
    - sconres: Senate Concurrent Resolution
    - hres: House Simple Resolution
    - sres: Senate Simple Resolution
    
    Args:
        bill_type: Bill type to validate
        field_name: Name of field being validated (for error messages)
        
    Returns:
        Validated bill type (lowercase)
        
    Raises:
        FieldValidationError: If bill type is invalid
        
    Example:
        >>> validate_bill_type("hr")  # Valid
        'hr'
        >>> validate_bill_type("HR")  # Valid (case insensitive)
        'hr'
        >>> validate_bill_type("invalid")  # Invalid
        FieldValidationError: Invalid bill_type 'invalid'
    """
    bill_type_lower = bill_type.lower()
    
    if bill_type_lower not in VALID_BILL_TYPES:
        logger.error(f"Invalid bill type: {bill_type}")
        raise FieldValidationError(
            f"Invalid bill_type '{bill_type}'. Must be one of: {', '.join(sorted(VALID_BILL_TYPES))}",
            field=field_name,
            value=bill_type,
            allowed_values=list(VALID_BILL_TYPES)
        )
    
    return bill_type_lower


# ============================================================================
# DATA FORMATTING HELPERS
# ============================================================================


def pretty_print_json(data: Any, indent: int = 2, filter_nulls: bool = False) -> None:
    """
    Pretty print nested JSON or model objects with class declarations preserved.
    
    Recursively pretty prints Python dicts, lists, JSON strings, or class instances
    with indentation. Handles nested structures and non-serializable objects gracefully.
    Optionally filters out keys with null (None) values, including in nested structures.
    
    NOTE: Preserves class object declarations (prints as ClassName({...})) for model objects.
    NOTE: Handles date/datetime objects by converting to ISO format strings.
    
    Args:
        data: The data to pretty print (dict, list, JSON string, or class instance)
        indent: Number of spaces for indentation (default: 2)
        filter_nulls: If True, remove keys with None values from dicts (default: False)
        
    Example:
        >>> from models.entities.bill import Bill
        >>> bill = Bill(congress=118, number=1, type="hr")
        >>> pretty_print_json(bill, indent=2, filter_nulls=True)
        Bill({
          "congress": 118,
          "number": 1,
          "type": "hr"
        })
    """

    # --- If input is a JSON string, parse it first ---
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            # If not valid JSON, just print the string
            print(data)
            return

    def _to_serializable(obj):
        """Convert date/datetime to an ISO string; pass everything else through."""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return obj

    def _filter_nulls(obj):
        """Recursively drop `None` values from dicts/lists/model objects."""
        if isinstance(obj, dict):
            # Only keep items where value is not None, and recursively filter
            return {k: _filter_nulls(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            # Recursively filter each item in the list
            return [_filter_nulls(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            # If it's an object, filter its __dict__ recursively and preserve class
            filtered = _filter_nulls(obj.__dict__)
            # Use a custom encoder for date/datetime
            return obj.__class__.__name__ + "(" + json.dumps(filtered, indent=indent, sort_keys=True, ensure_ascii=False, default=_to_serializable) + ")"
        else:
            # Convert date/datetime to string for JSON serialization
            return _to_serializable(obj)

    def _pretty(obj, level=0):
        """Recursively pretty-print, wrapping model objects as `ClassName({...})`."""
        # --- Handle model objects (with __dict__) ---
        if hasattr(obj, "__dict__") and not isinstance(obj, type):
            # Recursively pretty print the object's dict, but wrap in ClassName({...})
            class_name = obj.__class__.__name__
            # Optionally filter nulls
            d = obj.__dict__
            if filter_nulls:
                d = {k: v for k, v in d.items() if v is not None}
            pretty_inner = _pretty(d, level + 1)
            # Indent the inner dict for readability
            if isinstance(pretty_inner, str) and pretty_inner.startswith("{"):
                # Indent the dict block
                ind = " " * (indent * (level + 1))
                pretty_inner = "\n".join(ind + line if line.strip() else line for line in pretty_inner.splitlines())
                return f"{class_name}(\n{pretty_inner}\n{' ' * (indent * level)})"
            else:
                return f"{class_name}({pretty_inner})"
        elif isinstance(obj, dict):
            # Recursively pretty print dict
            items = []
            for k, v in obj.items():
                pretty_v = _pretty(v, level + 1)
                items.append(f"{json.dumps(k)}: {pretty_v}")
            if not items:
                return "{}"
            ind = " " * (indent * (level + 1))
            return "{\n" + ",\n".join(ind + item for item in items) + "\n" + " " * (indent * level) + "}"
        elif isinstance(obj, list):
            # Recursively pretty print list
            if not obj:
                return "[]"
            ind = " " * (indent * (level + 1))
            items = [ind + _pretty(item, level + 1) for item in obj]
            return "[\n" + ",\n".join(items) + "\n" + " " * (indent * level) + "]"
        else:
            # Fallback: use json.dumps for primitives, or str for others
            try:
                return json.dumps(obj, ensure_ascii=False, default=_to_serializable)
            except Exception:
                return str(obj)

    # --- Optionally filter out nulls before printing ---
    if filter_nulls:
        data = _filter_nulls(data)
        # If _filter_nulls returns a string (for model objects), just print it
        if isinstance(data, str) and "(" in data and data.endswith(")"):
            print(data)
            return

    # --- Use custom pretty printer to preserve class declarations ---
    print(_pretty(data))
