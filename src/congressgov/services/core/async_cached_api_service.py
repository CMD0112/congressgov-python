"""Async cached API service base class."""

from __future__ import annotations

from typing import Any, Dict, Optional
import logging

from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.cached_api_service import with_async_caching
from congressgov.services.caching import CacheConfig
from congressgov.services.caching.backends.base import CacheBackend
from congressgov.services.rate_limiting import RateLimiter, RateLimitConfig

logger = logging.getLogger(__name__)

__all__ = ["AsyncCachedApiService", "with_async_caching"]


class AsyncCachedApiService(AsyncApiService):
    """Base async service with caching and rate limiting."""

    def __init__(
        self,
        client: Optional[Any] = None,
        cache_config: Optional[CacheConfig] = None,
        cache_backend: Optional[CacheBackend] = None,
        rate_limiter: Optional[RateLimiter] = None,
        rate_limit_config: Optional[RateLimitConfig] = None,
        **kwargs: Any,
    ) -> None:
        self.client = client
        self.cache_config = cache_config
        self.cache_backend = cache_backend
        self.rate_limiter = rate_limiter
        self.rate_limit_config = rate_limit_config

        if self.cache_config and not self.cache_backend:
            from congressgov.services.core.cached_api_service import CachedApiService

            helper = CachedApiService(
                cache_config=cache_config,
                cache_backend=cache_backend,
                rate_limiter=rate_limiter,
                rate_limit_config=rate_limit_config,
            )
            self.cache_backend = helper.cache_backend
            if not self.rate_limiter:
                self.rate_limiter = helper.rate_limiter

        if self.rate_limit_config and not self.rate_limiter:
            from congressgov.services.core.cached_api_service import CachedApiService

            helper = CachedApiService(rate_limit_config=rate_limit_config)
            self.rate_limiter = helper.rate_limiter

    async def _apply_rate_limiting_async(self, endpoint: str = "default") -> bool:
        if not self.rate_limiter:
            return True
        try:
            return await self.rate_limiter.acquire_async(endpoint)
        except Exception as e:
            logger.warning("Rate limiting failed: %s", e)
            return True

    def get_cache_stats(self) -> Dict[str, Any]:
        if not self.cache_backend:
            return {}
        try:
            return self.cache_backend.get_stats()
        except Exception as e:
            logger.warning("Failed to get cache stats: %s", e)
            return {}
