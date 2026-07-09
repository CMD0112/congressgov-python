"""
Service-layer exception hierarchy

This module defines custom exceptions for congressgov.services, providing
clear, actionable error messages and proper exception chaining.

Exception Hierarchy:
    MiddlewareError (base)
    ├── ClientNotFoundError
    ├── ValidationError
    ├── APIError
    │   ├── RateLimitError
    │   └── TimeoutError
    └── ExpansionError

Usage:
    from congressgov.services.exceptions import ClientNotFoundError, APIError
    
    if client is None:
        raise ClientNotFoundError("No client available for API calls")
    
    try:
        response = api_call()
    except httpx.HTTPStatusError as e:
        raise APIError("API request failed", status_code=e.response.status_code) from e
"""

from __future__ import annotations
from typing import Optional, Any


class MiddlewareError(Exception):
    """
    Base exception for all service-layer errors.
    
    All custom service exceptions inherit from this class, allowing
    users to catch all congressgov.services-specific errors with a single except clause.
    
    Attributes:
        message: Human-readable error description
        details: Optional dictionary with additional error context
    """
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """
        Initialize service-layer error.
        
        Args:
            message: Human-readable error description
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation of error."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ClientNotFoundError(MiddlewareError):
    """
    Raised when no API client is available for operations.
    
    This error occurs when:
    - No client is provided to a method requiring API access
    - The target object has no client attribute
    - The service instance has no client configured
    
    Example:
        >>> service = Bill()  # No client configured
        >>> service.get(congress=118, bill_type="hr", bill_number=1)
        ClientNotFoundError: No client available. Provide client parameter or configure service instance.
    """
    
    def __init__(self, message: str = "No client available for API operations", **kwargs):
        """
        Initialize client not found error.
        
        Args:
            message: Error description
            **kwargs: Additional details to include in error context
        """
        super().__init__(message, details=kwargs)


class ValidationError(MiddlewareError):
    """
    Raised when input validation fails in the services layer.
    
    This error occurs when:
    - Required parameters are missing
    - Parameter values are outside valid ranges
    - Parameter types are incorrect
    - Parameter combinations are invalid
    
    Attributes:
        parameter: Name of the parameter that failed validation
        value: The invalid value that was provided
        constraint: Description of the validation constraint
        suggestions: List of suggested corrections (e.g., for typos)
        valid_values: List of all valid values for this parameter
    
    Example:
        >>> service.get(bill_type="invalid")
        ValidationError: Invalid bill type: 'invalid'
        Did you mean: 'hr', 's'?
        Valid values: 'hr', 's', 'hjres', 'sjres', 'hconres', 'sconres', 'hres', 'sres'
    """
    
    def __init__(
        self,
        message: str,
        parameter: Optional[str] = None,
        value: Optional[Any] = None,
        constraint: Optional[str] = None,
        suggestions: Optional[list[str]] = None,
        valid_values: Optional[list[str]] = None,
        **kwargs
    ):
        """
        Initialize validation error with helpful suggestions.
        
        Args:
            message: Error description
            parameter: Name of parameter that failed validation
            value: The invalid value
            constraint: Description of validation constraint
            suggestions: Suggested corrections (e.g., for typos)
            valid_values: List of all valid values for this parameter
            **kwargs: Additional details
        """
        details = kwargs
        if parameter:
            details['parameter'] = parameter
        if value is not None:
            details['value'] = value
        if constraint:
            details['constraint'] = constraint
        
        self.parameter = parameter
        self.value = value
        self.suggestions = suggestions or []
        self.valid_values = valid_values or []
        
        super().__init__(message, details=details)
    
    def __str__(self) -> str:
        """Format error message with suggestions."""
        base_msg = self.message
        
        if self.parameter:
            base_msg = f"Validation error for parameter '{self.parameter}': {base_msg}"
        
        parts = [base_msg]
        
        if self.suggestions:
            suggestions_str = ", ".join(f"'{s}'" for s in self.suggestions)
            parts.append(f"\nDid you mean: {suggestions_str}?")
        
        if self.valid_values:
            if len(self.valid_values) <= 10:
                valid_str = ", ".join(f"'{v}'" for v in self.valid_values)
                parts.append(f"\nValid values: {valid_str}")
            else:
                valid_str = ", ".join(f"'{v}'" for v in self.valid_values[:10])
                parts.append(f"\nValid values (showing first 10): {valid_str}, ...")
        
        return "".join(parts)


class APIError(MiddlewareError):
    """
    Raised when API requests fail.
    
    This error wraps HTTP errors and provides additional context about
    the failed request, including status codes, URLs, and request parameters.
    
    Attributes:
        status_code: HTTP status code (e.g., 404, 500)
        url: The URL that was requested
        method: HTTP method used (GET, POST, etc.)
        response_body: Response body if available
    
    Example:
        >>> try:
        ...     response = client.get("/invalid/endpoint")
        ... except httpx.HTTPStatusError as e:
        ...     raise APIError("API request failed", status_code=404) from e
    """
    
    def __init__(
        self,
        message: str = "API request failed",
        status_code: Optional[int] = None,
        url: Optional[str] = None,
        method: Optional[str] = None,
        response_body: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize API error.
        
        Args:
            message: Error description
            status_code: HTTP status code
            url: Requested URL
            method: HTTP method
            response_body: Response body text
            **kwargs: Additional details
        """
        details = kwargs
        if status_code:
            details['status_code'] = status_code
        if url:
            details['url'] = url
        if method:
            details['method'] = method
        if response_body:
            details['response_body'] = response_body
        super().__init__(message, details=details)


class RateLimitError(APIError):
    """
    Raised when API rate limit is exceeded.
    
    This error provides information about rate limits to help users
    implement appropriate retry logic or request throttling.
    
    Attributes:
        limit: Total rate limit (requests per period)
        remaining: Remaining requests in current period
        reset_time: When the rate limit resets (if available)
        retry_after: Seconds to wait before retrying
    
    Example:
        >>> if rate_limit_exceeded:
        ...     raise RateLimitError(
        ...         "Rate limit exceeded",
        ...         limit=1000,
        ...         remaining=0,
        ...         retry_after=60
        ...     )
    """
    
    def __init__(
        self,
        message: str = "API rate limit exceeded",
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
        reset_time: Optional[str] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize rate limit error.
        
        Args:
            message: Error description
            limit: Total rate limit
            remaining: Remaining requests
            reset_time: When limit resets
            retry_after: Seconds to wait
            **kwargs: Additional details
        """
        if limit is not None:
            kwargs['limit'] = limit
        if remaining is not None:
            kwargs['remaining'] = remaining
        if reset_time:
            kwargs['reset_time'] = reset_time
        if retry_after:
            kwargs['retry_after'] = retry_after
        super().__init__(message, status_code=429, **kwargs)


class TimeoutError(APIError):
    """
    Raised when API request times out.
    
    This error indicates that the request took too long to complete.
    Users should consider retrying with exponential backoff or checking
    their network connectivity.
    
    Attributes:
        timeout: Timeout duration in seconds
        elapsed: How long the request ran before timing out
    
    Example:
        >>> try:
        ...     response = client.get("/slow/endpoint", timeout=5.0)
        ... except httpx.TimeoutException as e:
        ...     raise TimeoutError("Request timed out", timeout=5.0) from e
    """
    
    def __init__(
        self,
        message: str = "API request timed out",
        timeout: Optional[float] = None,
        elapsed: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize timeout error.
        
        Args:
            message: Error description
            timeout: Configured timeout in seconds
            elapsed: Time elapsed before timeout
            **kwargs: Additional details
        """
        if timeout is not None:
            kwargs['timeout'] = timeout
        if elapsed is not None:
            kwargs['elapsed'] = elapsed
        super().__init__(message, status_code=408, **kwargs)


class UnsupportedApiUrlError(MiddlewareError):
    """Raised when a URL cannot be mapped to a known Congress.gov API route."""

    def __init__(self, message: str, *, url: str | None = None) -> None:
        self.url = url
        super().__init__(message)


class RequestStoreError(MiddlewareError):
    """
    Raised when the request store cannot read or write persisted responses.

    By default the store fails closed (no network fallback). Pass
    ``store_fail=True`` on the client or per-request to fall through to the API.
    """

    def __init__(
        self,
        message: str,
        *,
        request_key: str | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = dict(kwargs)
        if request_key:
            details["request_key"] = request_key
        if operation:
            details["operation"] = operation
        super().__init__(message, details=details)


class ExpansionError(MiddlewareError):
    """
    Raised when attribute expansion fails.
    
    This error occurs when expanding model attributes with additional
    API data fails due to missing parameters, invalid attributes,
    or API failures during expansion.
    
    Attributes:
        attribute: The attribute that failed to expand
        target_type: Type of the target object being expanded
        failed_attributes: List of attributes that failed (for batch operations)
    
    Example:
        >>> try:
        ...     expanded = service.expand(bill, attributes=["actions"])
        ... except ExpansionError as e:
        ...     print(f"Failed to expand: {e.attribute}")
    """
    
    def __init__(
        self,
        message: str,
        attribute: Optional[str] = None,
        target_type: Optional[str] = None,
        failed_attributes: Optional[list[str]] = None,
        **kwargs
    ):
        """
        Initialize expansion error.
        
        Args:
            message: Error description
            attribute: Attribute that failed to expand
            target_type: Type of target object
            failed_attributes: List of failed attributes
            **kwargs: Additional details
        """
        details = kwargs
        if attribute:
            details['attribute'] = attribute
        if target_type:
            details['target_type'] = target_type
        if failed_attributes:
            details['failed_attributes'] = failed_attributes
        super().__init__(message, details=details)


# === [PUBLIC API] ===
__all__ = [
    'MiddlewareError',
    'ClientNotFoundError',
    'ValidationError',
    'APIError',
    'RateLimitError',
    'TimeoutError',
    'ExpansionError',
    'RequestStoreError',
]
