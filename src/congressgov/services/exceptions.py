"""
Service-layer exceptions: `MiddlewareError` (base), with `ClientNotFoundError`,
`ValidationError`, `APIError` (and its `RateLimitError`/`TimeoutError` subclasses),
`ExpansionError`, `RequestStoreError`, and `UnsupportedApiUrlError` covering the
specific failure modes below.

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
    """Base class for every congressgov.services exception, so callers can catch
    all of them with a single `except MiddlewareError`.
    """

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ClientNotFoundError(MiddlewareError):
    """Raised when a service method needs an API client and none was provided
    or configured on the instance.

    Example:
        >>> service = Bill()  # No client configured
        >>> service.get(congress=118, bill_type="hr", bill_number=1)
        ClientNotFoundError: No client available. Provide client parameter or configure service instance.
    """

    def __init__(self, message: str = "No client available for API operations", **kwargs: Any) -> None:
        super().__init__(message, details=kwargs)


class ValidationError(MiddlewareError):
    """Raised for invalid input: missing/malformed/out-of-range parameters, or
    invalid parameter combinations. Carries `suggestions` and `valid_values` so
    the resulting message can point at likely typo fixes.

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
        **kwargs: Any,
    ) -> None:
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
    """Raised when an API request fails, wrapping the HTTP status code, URL,
    method, and response body for debugging.

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
        **kwargs: Any,
    ) -> None:
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
    """Raised when the Congress.gov API rate limit is exceeded. Carries `limit`,
    `remaining`, `reset_time`, and `retry_after` for building retry logic.

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
        **kwargs: Any,
    ) -> None:
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
    """Raised when an API request times out. Carries `timeout` (the configured
    limit) and `elapsed` (how long it actually ran).

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
        **kwargs: Any,
    ) -> None:
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
    """Raised when the request store cannot read or write persisted responses.

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
    """Raised when expanding a model's related attributes (fetching them from
    the API) fails, due to missing parameters, an invalid attribute name, or
    an API failure mid-expansion.

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
        **kwargs: Any,
    ) -> None:
        details = kwargs
        if attribute:
            details['attribute'] = attribute
        if target_type:
            details['target_type'] = target_type
        if failed_attributes:
            details['failed_attributes'] = failed_attributes
        super().__init__(message, details=details)


__all__ = [
    'MiddlewareError',
    'ClientNotFoundError',
    'ValidationError',
    'APIError',
    'RateLimitError',
    'TimeoutError',
    'ExpansionError',
    'RequestStoreError',
    'UnsupportedApiUrlError',
]
