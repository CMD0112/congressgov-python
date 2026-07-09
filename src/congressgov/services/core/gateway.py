"""
Extends the auto-generated Congress.gov API client with API-key header
injection and rate-limit tracking/enforcement.
"""

from __future__ import annotations

from typing import Any, Optional, Dict
import logging

from congressgov._client import Client
from congressgov.services.exceptions import RateLimitError

logger = logging.getLogger(__name__)


class ApiGateway(Client):
    """
    Enhanced API client with rate limiting and authentication management.
    
    This class extends the auto-generated Congress.gov API client to provide:
    - Automatic X-API-Key header injection
    - Rate limit tracking and enforcement
    - Clearer error messages for rate limit violations
    
    Attributes:
        ratelimit_default: Default rate limit value (requests per period)
        rate_limit_headers: Dictionary tracking current rate limit state
        
    Example:
        >>> gateway = ApiGateway(
        ...     base_url="https://api.congress.gov/v3",
        ...     api_key="your-api-key-here",
        ...     ratelimit_default=1000
        ... )
        >>> response = gateway.get_httpx_client().get("/bill")
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        **client_kwargs: Any
    ) -> None:
        """
        Initialize API gateway with authentication and rate limiting.
        
        The API key can be provided in three ways (in priority order):
        1. Explicit api_key parameter (highest priority)
        2. In headers dict of client_kwargs
        3. None (API will require key on requests)
        
        Args:
            base_url: Base URL for the Congress.gov API (e.g., "https://api.congress.gov/v3")
            api_key: Optional API key for authentication. If provided, automatically
                    added to headers as 'X-API-Key'
            **client_kwargs: Additional arguments passed to parent Client class
                ratelimit_default: (int) Default rate limit for tracking
                headers: (dict) Additional HTTP headers
                timeout: (float) Request timeout in seconds
                verify_ssl: (bool) Whether to verify SSL certificates
                
        Example:
            >>> # Explicit API key
            >>> gateway = ApiGateway(base_url="https://api.congress.gov/v3", api_key="key123")
            >>> 
            >>> # API key in headers
            >>> gateway = ApiGateway(
            ...     base_url="https://api.congress.gov/v3",
            ...     headers={"X-API-Key": "key123"}
            ... )
        """
        # === [HEADER HANDLING] ===
        # Extract headers from client_kwargs if present, else use empty dict
        # Use dict() to create a copy to avoid modifying caller's dict
        headers: Dict[str, str] = dict(client_kwargs.get('headers', {}))

        # === [API KEY INJECTION] ===
        # Priority order: explicit api_key parameter > existing header > None
        if api_key is not None:
            # Explicit api_key parameter takes precedence over existing header
            headers['X-API-Key'] = api_key
            logger.debug(f"Injected API key into headers (first {len(api_key)//2} chars)")
        elif 'X-API-Key' in headers:
            # API key already present in headers, leave it unchanged
            logger.debug("Using API key from existing headers")
        else:
            # No API key provided - API will likely require it on requests
            logger.warning("No API key provided. API requests may fail authentication")

        # Update client_kwargs with the possibly-updated headers
        client_kwargs['headers'] = headers

        # === [RATE LIMIT CONFIGURATION] ===
        # Extract rate limit default if provided, otherwise set to None
        if "ratelimit_default" in client_kwargs:
            self.ratelimit_default: Optional[int] = client_kwargs.pop("ratelimit_default")
            logger.info(f"Rate limit configured: {self.ratelimit_default} requests per period")
        else:
            self.ratelimit_default: Optional[int] = None
            logger.debug("No rate limit configured")

        # === [RATE LIMIT TRACKING] ===
        # Initialize rate limit tracking headers
        # None indicates rate limiting is not active/configured
        self.rate_limit_headers: Dict[str, Optional[int]] = {
            'x-ratelimit-limit': int(self.ratelimit_default) if self.ratelimit_default is not None else None,
            'x-ratelimit-remaining': int(self.ratelimit_default) if self.ratelimit_default is not None else None,
        }

        # === [PARENT INITIALIZATION] ===
        # Initialize parent Client with base_url and remaining kwargs
        super().__init__(base_url=base_url, **client_kwargs)
        
        logger.info(f"ApiGateway initialized with base_url={base_url}")

    def get_httpx_client(self) -> Any:
        """
        Get the underlying HTTPX client with rate limit enforcement.
        
        This method checks the rate limit before returning the client.
        If rate limit is exceeded, raises RateLimitError instead of
        returning the client.
        
        Returns:
            HTTPX client instance
            
        Raises:
            RateLimitError: If rate limit is exceeded (remaining requests <= 0)
            
        Example:
            >>> client = gateway.get_httpx_client()
            >>> response = client.get("/bill/118/hr/1")
        """
        # === [RATE LIMIT CHECK] ===
        # Only check rate limit if it is configured (not None)
        remaining = self.rate_limit_headers.get('x-ratelimit-remaining')
        
        if remaining is not None and int(remaining) <= 0:
            # Raise custom exception with details instead of generic Exception
            limit = self.rate_limit_headers.get('x-ratelimit-limit', 'unknown')
            logger.error(f"Rate limit exceeded: {remaining}/{limit} requests remaining")
            
            # Retry-After header parsing not implemented yet
            # The Congress.gov API doesn't consistently provide Retry-After headers
            # If needed in the future, parse from response headers passed to this method
            raise RateLimitError(
                "API rate limit exceeded",
                limit=limit,
                remaining=remaining,
                retry_after=None
            )
        
        # Log remaining requests if rate limiting is active
        if remaining is not None:
            logger.debug(f"Rate limit status: {remaining} requests remaining")

        # Return parent's httpx client
        return super().get_httpx_client()
    
    def update_rate_limit(self, limit: Optional[int] = None, remaining: Optional[int] = None) -> None:
        """
        Update rate limit tracking from response headers.
        
        This is a public method intended for use by congressgov.services
        to keep rate limit tracking synchronized with API responses.
        
        Call this method after receiving API responses to keep rate limit
        tracking synchronized with the server's actual limits.
        
        Args:
            limit: Total rate limit from X-RateLimit-Limit header
            remaining: Remaining requests from X-RateLimit-Remaining header
            
        Example:
            >>> response = client.get("/bill")
            >>> gateway.update_rate_limit(
            ...     limit=int(response.headers.get('X-RateLimit-Limit', 1000)),
            ...     remaining=int(response.headers.get('X-RateLimit-Remaining', 999))
            ... )
        """
        if limit is not None:
            self.rate_limit_headers['x-ratelimit-limit'] = limit
            logger.debug(f"Updated rate limit: {limit}")
        if remaining is not None:
            self.rate_limit_headers['x-ratelimit-remaining'] = remaining
            logger.debug(f"Updated rate remaining: {remaining}")
            
            # WARNING: Log if approaching rate limit
            if remaining < 100:
                logger.warning(f"Rate limit low: only {remaining} requests remaining")
