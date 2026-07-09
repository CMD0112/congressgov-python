"""
Custom exceptions for the models layer: `ModelError` (base), with
`ModelValidationError`, `ModelParsingError`, and `FieldValidationError` covering
validation failures, response-parsing failures, and single-field failures
respectively.

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
    """Base class for model-related errors, so callers can catch all of them at once."""

    def __init__(
        self,
        message: str,
        model_class: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.model_class = model_class
        self.details = details or {}

    def __str__(self) -> str:
        parts = [self.message]
        if self.model_class:
            parts.append(f"model={self.model_class}")
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            parts.append(details_str)
        return " (".join(parts) + ")" * (len(parts) - 1)


class ModelValidationError(ModelError):
    """Raised when model validation fails: missing required fields, type
    mismatches, or a failed model-level constraint.
    """

    def __init__(
        self,
        message: str,
        model_class: Optional[str] = None,
        errors: Optional[list[dict[str, Any]]] = None,
        input_data: Optional[dict[str, Any]] = None,
        **kwargs
    ):
        details = kwargs
        if errors:
            details['errors'] = errors
        if input_data:
            # Only the keys, not the values, to avoid leaking sensitive input in error details.
            details['input_data_keys'] = list(input_data.keys())
        super().__init__(message, model_class=model_class, details=details)


class ModelParsingError(ModelError):
    """Raised when parsing an API response into a model fails: unexpected
    response shape, a type that can't be coerced, a missing envelope key, or
    invalid JSON.
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
        details = kwargs
        if parse_stage:
            details['parse_stage'] = parse_stage
        if expected_structure:
            details['expected_structure'] = expected_structure
        if raw_data_type:
            details['raw_data_type'] = raw_data_type
        super().__init__(message, model_class=model_class, details=details)


class FieldValidationError(ModelError):
    """Raised when a single field fails validation, e.g. from a `@field_validator`:

        @field_validator('congress')
        @classmethod
        def validate_congress(cls, v: int) -> int:
            if v < 1:
                raise FieldValidationError(
                    "Congress number must be positive",
                    field='congress',
                    value=v,
                    constraint='congress >= 1'
                )
            return v
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
        details = kwargs
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)  # stringify so complex types don't break serialization
        if constraint:
            details['constraint'] = constraint
        if allowed_values:
            details['allowed_values'] = allowed_values
        super().__init__(message, model_class=model_class, details=details)


__all__ = [
    'ModelError',
    'ModelValidationError',
    'ModelParsingError',
    'FieldValidationError',
]



