from __future__ import annotations
from typing import Any
from .model import Model


class CountRef(Model):
    """A count + URL pair, used where the API gives a total instead of the full list."""
    count: int | None = None
    url: str | None = None


class URL(Model):
    """A URL value that accepts a plain string, a `{"url": ...}` dict, or another
    `URL` instance, and normalizes all of them to the same shape. Any model field
    typed as `URL` gets this conversion automatically via the core schema hook below.
    """
    url: Any | None = None

    @classmethod
    def model_validate(cls, value: Any) -> "URL":
        """Accept a string, dict, `URL` instance, or list of any of those."""
        if isinstance(value, list):
            return [cls.model_validate(item) for item in value]
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            return cls(url=value)
        if isinstance(value, dict):
            return super().model_validate(value)
        return super().model_validate(value)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        """Wrap the standard model schema with a before-validator so any field
        typed as `URL` accepts a plain string or dict, not just a `URL` instance.
        """
        from pydantic_core import core_schema

        def validate_url(value: Any) -> Any:
            if value is None:
                return None
            if isinstance(value, cls):
                return value
            if isinstance(value, str):
                return cls(url=value)
            if isinstance(value, dict):
                return value
            return value

        python_schema = handler(source_type)
        return core_schema.no_info_before_validator_function(
            validate_url,
            python_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.url if isinstance(instance, cls) else instance
            ),
        )


class PolicyArea(Model):
    """Policy area classification (e.g. "Health", "Agriculture and Food")."""
    name: str | None = None
