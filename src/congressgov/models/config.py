"""
Models Configuration Module

Centralized configuration for models layer settings including
validation rules, parsing options, and default values.

Usage:
    from models.config import MODELS_CONFIG, STRICT_VALIDATION
    
    # Check if strict validation is enabled
    if STRICT_VALIDATION:
        validate_all_fields(data)
"""

from __future__ import annotations

from typing import Any, Dict
import logging


# ============================================================================
# VALIDATION CONFIGURATION
# ============================================================================

# Enable strict validation mode
# NOTE: In strict mode, all validation errors cause exceptions
# In non-strict mode, validation warnings are logged but processing continues
STRICT_VALIDATION = True

# Validate congress numbers are in valid range
VALIDATE_CONGRESS_RANGE = True

# Validate dates are not in the future
VALIDATE_DATE_RANGES = True

# Validate enum values match expected choices
VALIDATE_ENUM_VALUES = True

# Validate URL formats
VALIDATE_URL_FORMATS = False  # Can be expensive, disabled by default

# Validate required fields are present
VALIDATE_REQUIRED_FIELDS = True


# ============================================================================
# PARSING CONFIGURATION
# ============================================================================

# Enable automatic datetime string parsing
AUTO_PARSE_DATETIME = True

# Enable automatic date string parsing
AUTO_PARSE_DATE = True

# Enable automatic envelope unwrapping
AUTO_UNWRAP_ENVELOPES = True

# Enable automatic single-key unwrapping
AUTO_UNWRAP_SINGLE_KEYS = True

# Enable debug mode for model validation
DEBUG_MODEL_VALIDATION = False

# Enable debug mode for envelope unwrapping
DEBUG_ENVELOPE_UNWRAPPING = False


# ============================================================================
# DEFAULT VALUES CONFIGURATION
# ============================================================================

# Default value for congress number when not specified
DEFAULT_CONGRESS = None

# Default value for chamber when not specified
DEFAULT_CHAMBER = None

# Default value for pagination limit
DEFAULT_MODEL_LIMIT = 20


# ============================================================================
# FIELD DOCUMENTATION CONFIGURATION
# ============================================================================

# Include field descriptions in model schema
INCLUDE_FIELD_DESCRIPTIONS = True

# Include field examples in model schema
INCLUDE_FIELD_EXAMPLES = True

# Include field constraints in model schema
INCLUDE_FIELD_CONSTRAINTS = True


# ============================================================================
# SERIALIZATION CONFIGURATION
# ============================================================================

# Use camelCase for field aliases (matches API response format)
USE_CAMEL_CASE_ALIASES = True

# Allow population by field name (in addition to alias)
ALLOW_POPULATE_BY_NAME = True

# Exclude None values from serialization
EXCLUDE_NONE = False

# Exclude unset values from serialization
EXCLUDE_UNSET = False

# Use enum values instead of enum objects in serialization
USE_ENUM_VALUES = True

# Validate default values
VALIDATE_DEFAULT_VALUES = True


# ============================================================================
# MODEL BEHAVIOR CONFIGURATION
# ============================================================================

# Allow extra fields not defined in model
ALLOW_EXTRA_FIELDS = True  # API may add new fields

# Extra fields behavior: "allow", "forbid", or "ignore"
EXTRA_FIELDS_BEHAVIOR = "ignore"

# Make models frozen (immutable) after creation
FROZEN_MODELS = False

# Validate assignment to model fields
VALIDATE_ASSIGNMENT = False  # Can impact performance

# Use smart union matching for Union types
SMART_UNION = True

# Arbitrary types allowed in models
ARBITRARY_TYPES_ALLOWED = False


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Default logging level for model modules
DEFAULT_LOG_LEVEL = logging.WARNING

# Log validation errors
LOG_VALIDATION_ERRORS = True

# Log validation warnings
LOG_VALIDATION_WARNINGS = True

# Log parsing errors
LOG_PARSING_ERRORS = True

# Log model creation
LOG_MODEL_CREATION = False  # Can be verbose


# ============================================================================
# PERFORMANCE CONFIGURATION
# ============================================================================

# Enable model caching
ENABLE_MODEL_CACHING = False

# Maximum cache size for model instances
MAX_MODEL_CACHE_SIZE = 1000

# Enable lazy loading for relationships
ENABLE_LAZY_LOADING = False

# Enable model validation caching
CACHE_VALIDATION_RESULTS = False


# ============================================================================
# CONSOLIDATED CONFIGURATION DICTIONARY
# ============================================================================

MODELS_CONFIG: Dict[str, Any] = {
    "validation": {
        "strict": STRICT_VALIDATION,
        "congress_range": VALIDATE_CONGRESS_RANGE,
        "date_ranges": VALIDATE_DATE_RANGES,
        "enum_values": VALIDATE_ENUM_VALUES,
        "url_formats": VALIDATE_URL_FORMATS,
        "required_fields": VALIDATE_REQUIRED_FIELDS,
    },
    "parsing": {
        "auto_parse_datetime": AUTO_PARSE_DATETIME,
        "auto_parse_date": AUTO_PARSE_DATE,
        "auto_unwrap_envelopes": AUTO_UNWRAP_ENVELOPES,
        "auto_unwrap_single_keys": AUTO_UNWRAP_SINGLE_KEYS,
        "debug_validation": DEBUG_MODEL_VALIDATION,
        "debug_unwrapping": DEBUG_ENVELOPE_UNWRAPPING,
    },
    "defaults": {
        "congress": DEFAULT_CONGRESS,
        "chamber": DEFAULT_CHAMBER,
        "limit": DEFAULT_MODEL_LIMIT,
    },
    "documentation": {
        "include_descriptions": INCLUDE_FIELD_DESCRIPTIONS,
        "include_examples": INCLUDE_FIELD_EXAMPLES,
        "include_constraints": INCLUDE_FIELD_CONSTRAINTS,
    },
    "serialization": {
        "use_camel_case": USE_CAMEL_CASE_ALIASES,
        "populate_by_name": ALLOW_POPULATE_BY_NAME,
        "exclude_none": EXCLUDE_NONE,
        "exclude_unset": EXCLUDE_UNSET,
        "use_enum_values": USE_ENUM_VALUES,
        "validate_defaults": VALIDATE_DEFAULT_VALUES,
    },
    "behavior": {
        "allow_extra": ALLOW_EXTRA_FIELDS,
        "extra_behavior": EXTRA_FIELDS_BEHAVIOR,
        "frozen": FROZEN_MODELS,
        "validate_assignment": VALIDATE_ASSIGNMENT,
        "smart_union": SMART_UNION,
        "arbitrary_types": ARBITRARY_TYPES_ALLOWED,
    },
    "logging": {
        "default_level": DEFAULT_LOG_LEVEL,
        "log_validation_errors": LOG_VALIDATION_ERRORS,
        "log_validation_warnings": LOG_VALIDATION_WARNINGS,
        "log_parsing_errors": LOG_PARSING_ERRORS,
        "log_model_creation": LOG_MODEL_CREATION,
    },
    "performance": {
        "enable_caching": ENABLE_MODEL_CACHING,
        "max_cache_size": MAX_MODEL_CACHE_SIZE,
        "lazy_loading": ENABLE_LAZY_LOADING,
        "cache_validation": CACHE_VALIDATION_RESULTS,
    },
}


# ============================================================================
# CONFIGURATION HELPERS
# ============================================================================


def is_validation_enabled(validation_type: str = "strict") -> bool:
    """
    Check if a specific validation type is enabled.
    
    Args:
        validation_type: Type of validation to check
        
    Returns:
        True if validation is enabled
        
    Example:
        >>> is_validation_enabled("congress_range")
        True
    """
    return MODELS_CONFIG["validation"].get(validation_type, False)


def should_log(log_type: str) -> bool:
    """
    Check if a specific log type should be logged.
    
    Args:
        log_type: Type of logging to check
        
    Returns:
        True if logging is enabled for this type
        
    Example:
        >>> should_log("validation_errors")
        True
    """
    key = f"log_{log_type}"
    return MODELS_CONFIG["logging"].get(key, False)


def get_pydantic_config() -> Dict[str, Any]:
    """
    Get Pydantic ConfigDict based on models configuration.
    
    Returns:
        Dictionary suitable for Pydantic ConfigDict
        
    Example:
        >>> from pydantic import BaseModel, ConfigDict
        >>> class MyModel(BaseModel):
        ...     model_config = ConfigDict(**get_pydantic_config())
    """
    from pydantic.alias_generators import to_camel
    
    return {
        "alias_generator": to_camel if USE_CAMEL_CASE_ALIASES else None,
        "populate_by_name": ALLOW_POPULATE_BY_NAME,
        "extra": EXTRA_FIELDS_BEHAVIOR,
        "frozen": FROZEN_MODELS,
        "validate_default": VALIDATE_DEFAULT_VALUES,
        "use_enum_values": USE_ENUM_VALUES,
        "validate_assignment": VALIDATE_ASSIGNMENT,
        "arbitrary_types_allowed": ARBITRARY_TYPES_ALLOWED,
    }


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    # Configuration dictionary
    'MODELS_CONFIG',
    
    # Validation constants
    'STRICT_VALIDATION',
    'VALIDATE_CONGRESS_RANGE',
    'VALIDATE_DATE_RANGES',
    'VALIDATE_ENUM_VALUES',
    'VALIDATE_URL_FORMATS',
    'VALIDATE_REQUIRED_FIELDS',
    
    # Parsing constants
    'AUTO_PARSE_DATETIME',
    'AUTO_PARSE_DATE',
    'AUTO_UNWRAP_ENVELOPES',
    'DEBUG_MODEL_VALIDATION',
    
    # Default values
    'DEFAULT_CONGRESS',
    'DEFAULT_CHAMBER',
    'DEFAULT_MODEL_LIMIT',
    
    # Serialization constants
    'USE_CAMEL_CASE_ALIASES',
    'ALLOW_POPULATE_BY_NAME',
    'USE_ENUM_VALUES',
    
    # Behavior constants
    'ALLOW_EXTRA_FIELDS',
    'FROZEN_MODELS',
    'VALIDATE_ASSIGNMENT',
    
    # Helper functions
    'is_validation_enabled',
    'should_log',
    'get_pydantic_config',
]



