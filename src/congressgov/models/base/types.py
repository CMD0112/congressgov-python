from __future__ import annotations
from typing import Any
from .model import Model

# === [GENERIC TYPES] Basic, domain-independent classes ===

class CountRef(Model):
    """Reference to a count and URL for pagination/links"""
    count: int | None = None
    url: str | None = None


# CountRef.model_rebuild()  # Handled by centralized rebuild system


class URL(Model):
    """
    === [FLEXIBLE URL TYPE] ===
    A flexible URL type that automatically converts strings to URL instances.
    
    This class integrates with Pydantic v2's validation system to handle:
    - Plain strings (e.g., "https://api.congress.gov/...")
    - Dictionaries with a 'url' key
    - Existing URL instances (passthrough)
    
    The field validator ensures that anywhere URL is used as a type annotation,
    string values will be automatically converted to URL instances.
    """
    url: Any | None = None

    @classmethod
    def model_validate(cls, value: Any) -> "URL":
        """
        === [FLEXIBLE VALIDATION FOR URL] ===
        Allows this class to be used as a Pydantic field and accept either:
        - a plain string (interpreted as the URL)
        - a dict (with a 'url' key)
        - an instance of URL (idempotent)
        - a list of any of the above (returns a list of URL instances)
        This enables seamless integration as a value object in other models.
        """
        # === [LIST CASE] ===
        if isinstance(value, list):
            # Recursively validate each item in the list
            return [cls.model_validate(item) for item in value]
        # === [ALREADY URL INSTANCE] ===
        if isinstance(value, cls):
            return value
        # === [PLAIN STRING CASE] ===
        if isinstance(value, str):
            return cls(url=value)
        # === [DICT CASE] ===
        if isinstance(value, dict):
            return super().model_validate(value)
        # === [FALLBACK TO DEFAULT MODEL VALIDATION] ===
        return super().model_validate(value)
    
    # === [PYDANTIC V2 VALIDATION HOOK] ===
    # This validator runs for ANY field typed as URL in other models
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        """
        === [CUSTOM PYDANTIC CORE SCHEMA] ===
        Integrates URL with Pydantic v2's validation system.
        This ensures that string URLs are automatically converted to URL instances
        whenever URL is used as a type annotation in any model.
        
        Uses a before-validator approach to convert strings to URL instances
        before standard Pydantic validation runs.
        """
        from pydantic_core import core_schema
        
        def validate_url(value: Any) -> Any:
            """
            Convert strings and dicts to proper format for URL validation.
            This runs BEFORE Pydantic's standard validation.
            """
            if value is None:
                return None
            # If already a URL instance, return as-is
            if isinstance(value, cls):
                return value
            # Convert string to URL instance directly
            if isinstance(value, str):
                return cls(url=value)
            # Dict should be validated normally
            if isinstance(value, dict):
                # Return dict for standard model validation
                return value
            # For anything else, return as-is and let Pydantic handle it
            return value
        
        # Get the standard schema for this model using the handler
        # This prevents recursion by using Pydantic's default model schema
        python_schema = handler(source_type)
        
        # Wrap it with our before-validator
        return core_schema.no_info_before_validator_function(
            validate_url,
            python_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.url if isinstance(instance, cls) else instance
            ),
        )


# URL.model_rebuild()  # Handled by centralized rebuild system


class PolicyArea(Model):
    """Policy area classification"""
    name: str | None = None


# PolicyArea.model_rebuild()  # Handled by centralized rebuild system
