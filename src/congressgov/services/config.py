"""
Congress.gov services configuration module

Centralized configuration for congressgov.services settings including
timeouts, retry policies, logging configuration, and API limits.

Usage:
    from congressgov.services.config import MIDDLEWARE_CONFIG, DEFAULT_TIMEOUT
    
    # Use default timeout
    response = api_function(timeout=DEFAULT_TIMEOUT)
    
    # Access configuration
    retry_attempts = MIDDLEWARE_CONFIG['retry']['max_attempts']
"""

from __future__ import annotations

from typing import Any, Dict
import logging


# ============================================================================
# TIMEOUT CONFIGURATION
# ============================================================================

# Default timeout for API requests (in seconds)
# NOTE: Congress.gov API can be slow, so we use a generous timeout
DEFAULT_TIMEOUT = 30.0

# Timeout for quick operations (metadata, existence checks)
QUICK_TIMEOUT = 10.0

# Timeout for bulk operations (large result sets)
BULK_TIMEOUT = 60.0

# Connection timeout (separate from read timeout)
CONNECTION_TIMEOUT = 5.0


# ============================================================================
# RETRY POLICY CONFIGURATION
# ============================================================================

# Maximum number of retry attempts for failed requests
MAX_RETRY_ATTEMPTS = 3

# Initial backoff delay (in seconds)
INITIAL_BACKOFF = 1.0

# Maximum backoff delay (in seconds)
MAX_BACKOFF = 30.0

# Backoff multiplier for exponential backoff
BACKOFF_MULTIPLIER = 2.0

# HTTP status codes that should trigger a retry
RETRYABLE_STATUS_CODES = {
    408,  # Request Timeout
    429,  # Too Many Requests (Rate Limit)
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
}


# ============================================================================
# RATE LIMIT CONFIGURATION
# ============================================================================

# Default rate limit (requests per hour)
# NOTE: Congress.gov API allows 1000 requests per hour per API key
DEFAULT_RATE_LIMIT = 1000

# WARNING threshold for rate limit (percentage)
# Warn when remaining requests fall below this percentage
RATE_LIMIT_WARNING_THRESHOLD = 0.10  # 10%

# CRITICAL threshold for rate limit (percentage)
# Log critical warning when remaining requests fall below this percentage
RATE_LIMIT_CRITICAL_THRESHOLD = 0.05  # 5%


# ============================================================================
# PAGINATION CONFIGURATION
# ============================================================================

# Default limit for paginated requests
DEFAULT_PAGINATION_LIMIT = 20

# Maximum limit for paginated requests
MAX_PAGINATION_LIMIT = 250

# Default offset for paginated requests
DEFAULT_PAGINATION_OFFSET = 0


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Default logging level for service modules
DEFAULT_LOG_LEVEL = logging.INFO

# Logging format string
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Date format for logs
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Whether to log API request parameters (disable in production for security)
LOG_API_PARAMETERS = False

# Whether to log API response bodies (can be verbose, disable in production)
LOG_API_RESPONSES = False


# ============================================================================
# CACHING CONFIGURATION
# ============================================================================

# Enable response caching (if caching backend is available)
ENABLE_CACHING = False

# Default cache TTL (time to live) in seconds
DEFAULT_CACHE_TTL = 3600  # 1 hour

# Cache TTL for static/rarely-changing data
STATIC_CACHE_TTL = 86400  # 24 hours

# Cache TTL for frequently-changing data
DYNAMIC_CACHE_TTL = 300  # 5 minutes


# ============================================================================
# EXPANSION CONFIGURATION
# ============================================================================

# Maximum number of attributes to expand in a single operation
MAX_EXPANSION_ATTRIBUTES = 10

# Whether to continue expansion if one attribute fails
CONTINUE_ON_EXPANSION_ERROR = True

# Whether to return detailed expansion results by default
RETURN_DETAILED_EXPANSION_RESULTS = False


# ============================================================================
# VALIDATION CONFIGURATION
# ============================================================================

# Whether to validate parameters before API calls
ENABLE_PARAMETER_VALIDATION = True

# Whether to validate response data after API calls
ENABLE_RESPONSE_VALIDATION = True

# Whether to allow future congress numbers
ALLOW_FUTURE_CONGRESS = False

# Whether to allow future dates
ALLOW_FUTURE_DATES = False


# ============================================================================
# CONSOLIDATED CONFIGURATION DICTIONARY
# ============================================================================

MIDDLEWARE_CONFIG: Dict[str, Any] = {
    "timeout": {
        "default": DEFAULT_TIMEOUT,
        "quick": QUICK_TIMEOUT,
        "bulk": BULK_TIMEOUT,
        "connection": CONNECTION_TIMEOUT,
    },
    "retry": {
        "max_attempts": MAX_RETRY_ATTEMPTS,
        "initial_backoff": INITIAL_BACKOFF,
        "max_backoff": MAX_BACKOFF,
        "backoff_multiplier": BACKOFF_MULTIPLIER,
        "retryable_status_codes": RETRYABLE_STATUS_CODES,
    },
    "rate_limit": {
        "default": DEFAULT_RATE_LIMIT,
        "warning_threshold": RATE_LIMIT_WARNING_THRESHOLD,
        "critical_threshold": RATE_LIMIT_CRITICAL_THRESHOLD,
    },
    "pagination": {
        "default_limit": DEFAULT_PAGINATION_LIMIT,
        "max_limit": MAX_PAGINATION_LIMIT,
        "default_offset": DEFAULT_PAGINATION_OFFSET,
    },
    "logging": {
        "default_level": DEFAULT_LOG_LEVEL,
        "format": LOG_FORMAT,
        "date_format": LOG_DATE_FORMAT,
        "log_parameters": LOG_API_PARAMETERS,
        "log_responses": LOG_API_RESPONSES,
    },
    "caching": {
        "enabled": ENABLE_CACHING,
        "default_ttl": DEFAULT_CACHE_TTL,
        "static_ttl": STATIC_CACHE_TTL,
        "dynamic_ttl": DYNAMIC_CACHE_TTL,
    },
    "expansion": {
        "max_attributes": MAX_EXPANSION_ATTRIBUTES,
        "continue_on_error": CONTINUE_ON_EXPANSION_ERROR,
        "return_detailed_results": RETURN_DETAILED_EXPANSION_RESULTS,
    },
    "validation": {
        "enable_parameter_validation": ENABLE_PARAMETER_VALIDATION,
        "enable_response_validation": ENABLE_RESPONSE_VALIDATION,
        "allow_future_congress": ALLOW_FUTURE_CONGRESS,
        "allow_future_dates": ALLOW_FUTURE_DATES,
    },
}


# ============================================================================
# CONFIGURATION HELPERS
# ============================================================================


def get_timeout(operation_type: str = "default") -> float:
    """
    Get timeout value for specific operation type.
    
    Args:
        operation_type: Type of operation ("default", "quick", "bulk")
        
    Returns:
        Timeout in seconds
        
    Example:
        >>> timeout = get_timeout("bulk")
        60.0
    """
    return MIDDLEWARE_CONFIG["timeout"].get(operation_type, DEFAULT_TIMEOUT)


def should_retry(status_code: int) -> bool:
    """
    Determine if request should be retried based on status code.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        True if request should be retried
        
    Example:
        >>> should_retry(503)  # Service Unavailable
        True
        >>> should_retry(404)  # Not Found
        False
    """
    return status_code in RETRYABLE_STATUS_CODES


def calculate_backoff(attempt: int) -> float:
    """
    Calculate backoff delay for retry attempt.
    
    Uses exponential backoff: delay = initial_backoff * (multiplier ^ attempt)
    
    Args:
        attempt: Current retry attempt number (0-indexed)
        
    Returns:
        Backoff delay in seconds (capped at MAX_BACKOFF)
        
    Example:
        >>> calculate_backoff(0)  # First retry
        1.0
        >>> calculate_backoff(1)  # Second retry
        2.0
        >>> calculate_backoff(2)  # Third retry
        4.0
    """
    delay = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** attempt)
    return min(delay, MAX_BACKOFF)


def configure_logging(level: int | None = None) -> None:
    """Configure root logging for congressgov.services (idempotent)."""
    logging.basicConfig(
        level=level if level is not None else DEFAULT_LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        force=True,
    )


def is_rate_limit_low(remaining: int, limit: int) -> bool:
    """
    Check if rate limit is running low.
    
    Args:
        remaining: Remaining requests
        limit: Total rate limit
        
    Returns:
        True if remaining is below warning threshold
        
    Example:
        >>> is_rate_limit_low(50, 1000)  # 5% remaining
        True
        >>> is_rate_limit_low(200, 1000)  # 20% remaining
        False
    """
    if limit == 0:
        return False
    percentage = remaining / limit
    return percentage < RATE_LIMIT_WARNING_THRESHOLD


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    # Configuration dictionary
    'MIDDLEWARE_CONFIG',
    
    # Timeout constants
    'DEFAULT_TIMEOUT',
    'QUICK_TIMEOUT',
    'BULK_TIMEOUT',
    'CONNECTION_TIMEOUT',
    
    # Retry constants
    'MAX_RETRY_ATTEMPTS',
    'INITIAL_BACKOFF',
    'MAX_BACKOFF',
    'BACKOFF_MULTIPLIER',
    'RETRYABLE_STATUS_CODES',
    
    # Rate limit constants
    'DEFAULT_RATE_LIMIT',
    'RATE_LIMIT_WARNING_THRESHOLD',
    'RATE_LIMIT_CRITICAL_THRESHOLD',
    
    # Pagination constants
    'DEFAULT_PAGINATION_LIMIT',
    'MAX_PAGINATION_LIMIT',
    'DEFAULT_PAGINATION_OFFSET',
    
    # Logging constants
    'DEFAULT_LOG_LEVEL',
    'LOG_FORMAT',
    'LOG_DATE_FORMAT',
    'LOG_API_PARAMETERS',
    'LOG_API_RESPONSES',
    'configure_logging',
    
    # Caching constants
    'ENABLE_CACHING',
    'DEFAULT_CACHE_TTL',
    
    # Expansion constants
    'MAX_EXPANSION_ATTRIBUTES',
    'CONTINUE_ON_EXPANSION_ERROR',
    
    # Validation constants
    'ENABLE_PARAMETER_VALIDATION',
    'ENABLE_RESPONSE_VALIDATION',
    
    # Helper functions
    'get_timeout',
    'should_retry',
    'calculate_backoff',
    'is_rate_limit_low',
]
