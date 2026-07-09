"""
Model Exception Hierarchy

This module defines custom exceptions for the models layer, providing
clear error messages for data validation and parsing issues.

Exception Hierarchy:
    ModelError (base)
    ├── ModelValidationError
    ├── ModelParsingError
    └── FieldValidationError

Usage:
    from models.exceptions import FieldValidationError
    
    @field_validator('congress')
    @classmethod
    def validate_congress(cls, v: int) -> int:
        if v < 1:
            raise FieldValidationError(
                "Congress number must be >= 1",
                field='congress',
                value=v,
                constraint='congress >= 1'
            )
        return v
"""

from __future__ import annotations
from typing import Optional, Any


class ModelError(Exception):
    """
    Base exception for all model-related errors.
    
    All custom model exceptions inherit from this class, allowing
    users to catch all model-specific errors with a single except clause.
    
    Attributes:
        message: Human-readable error description
        model_class: The model class where the error occurred
        details: Optional dictionary with additional error context
    """
    
    def __init__(
        self,
        message: str,
        model_class: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ):
        """
        Initialize model error.
        
        Args:
            message: Human-readable error description
            model_class: Name of the model class where error occurred
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.model_class = model_class
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation of error."""
        parts = [self.message]
        if self.model_class:
            parts.append(f"model={self.model_class}")
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            parts.append(details_str)
        return " (".join(parts) + ")" * (len(parts) - 1)


class ModelValidationError(ModelError):
    """
    Raised when model validation fails.
    
    This error occurs when:
    - Required fields are missing
    - Field types don't match expectations
    - Multiple validation rules fail
    - Model-level validation constraints fail
    
    Attributes:
        errors: List of validation error details
        input_data: The data that failed validation (sanitized)
    
    Example:
        >>> try:
        ...     bill = Bill.model_validate(invalid_data)
        ... except ModelValidationError as e:
        ...     print(f"Validation failed for {e.model_class}: {e.errors}")
    """
    
    def __init__(
        self,
        message: str,
        model_class: Optional[str] = None,
        errors: Optional[list[dict[str, Any]]] = None,
        input_data: Optional[dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize model validation error.
        
        Args:
            message: Error description
            model_class: Name of model class
            errors: List of validation errors
            input_data: Input data that failed validation
            **kwargs: Additional details
        """
        details = kwargs
        if errors:
            details['errors'] = errors
        if input_data:
            # NOTE: Sanitize input data to avoid exposing sensitive information
            details['input_data_keys'] = list(input_data.keys())
        super().__init__(message, model_class=model_class, details=details)


class ModelParsingError(ModelError):
    """
    Raised when parsing API response data into models fails.
    
    This error occurs when:
    - API response structure is unexpected
    - Data cannot be coerced to expected types
    - Required envelope keys are missing
    - JSON parsing fails
    
    Attributes:
        raw_data: The raw data that failed to parse (sanitized)
        parse_stage: Which parsing stage failed
        expected_structure: What structure was expected
    
    Example:
        >>> try:
        ...     result = parse_api_response(response)
        ... except ModelParsingError as e:
        ...     print(f"Parse failed at {e.parse_stage}: {e.message}")
    """
    
    def __init__(
        self,
        message: str,
        model_class: Optional[str] = None,
        parse_stage: Optional[str] = None,
        expected_structure: Optional[str] = None,
        raw_data_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize model parsing error.
        
        Args:
            message: Error description
            model_class: Name of model class
            parse_stage: Stage where parsing failed
            expected_structure: Expected data structure
            raw_data_type: Type of raw data received
            **kwargs: Additional details
        """
        details = kwargs
        if parse_stage:
            details['parse_stage'] = parse_stage
        if expected_structure:
            details['expected_structure'] = expected_structure
        if raw_data_type:
            details['raw_data_type'] = raw_data_type
        super().__init__(message, model_class=model_class, details=details)


class FieldValidationError(ModelError):
    """
    Raised when a specific field fails validation.
    
    This error provides detailed information about individual field
    validation failures, making it easy to identify and fix data issues.
    
    Attributes:
        field: Name of the field that failed validation
        value: The invalid value that was provided
        constraint: Description of the validation constraint
        allowed_values: List of allowed values (for enums/choices)
    
    Example:
        >>> @field_validator('congress')
        ... @classmethod
        ... def validate_congress(cls, v: int) -> int:
        ...     if v < 1:
        ...         raise FieldValidationError(
        ...             "Congress number must be positive",
        ...             field='congress',
        ...             value=v,
        ...             constraint='congress >= 1'
        ...         )
        ...     return v
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        constraint: Optional[str] = None,
        allowed_values: Optional[list[Any]] = None,
        model_class: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize field validation error.
        
        Args:
            message: Error description
            field: Name of field that failed
            value: Invalid value provided
            constraint: Validation constraint description
            allowed_values: List of allowed values
            model_class: Name of model class
            **kwargs: Additional details
        """
        details = kwargs
        if field:
            details['field'] = field
        if value is not None:
            # NOTE: Convert value to string to avoid issues with complex types
            details['value'] = str(value)
        if constraint:
            details['constraint'] = constraint
        if allowed_values:
            details['allowed_values'] = allowed_values
        super().__init__(message, model_class=model_class, details=details)


# === [PUBLIC API] ===
__all__ = [
    'ModelError',
    'ModelValidationError',
    'ModelParsingError',
    'FieldValidationError',
]



