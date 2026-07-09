"""
Cached API service base class.

This module provides a base class for API services that integrates
caching and rate limiting with the existing service architecture.
"""

from __future__ import annotations

from typing import Any, Optional, Dict
import logging
import time
from functools import wraps

from .api_service import ApiService
from ..caching import CacheConfig
from ..caching.backends.base import CacheBackend
from ..rate_limiting import RateLimiter, RateLimitConfig

logger = logging.getLogger(__name__)


class CachedApiService(ApiService):
    """
    Base class for API services with integrated caching and rate limiting.

    .. deprecated::
        Use :func:`congressgov.get_client_from_env` with the request store
        (blob lane) instead. ``CachedApiService`` is not wired into the
        unified workspace and will be removed in a future release.
    """
    
    def __init__(
        self,
        client: Optional[Any] = None,
        cache_config: Optional[CacheConfig] = None,
        cache_backend: Optional[CacheBackend] = None,
        rate_limiter: Optional[RateLimiter] = None,
        rate_limit_config: Optional[RateLimitConfig] = None,
        **kwargs
    ):
        """
        Initialize cached API service.
        
        Args:
            client: API client instance
            cache_config: Cache configuration
            cache_backend: Cache backend instance
            rate_limiter: Rate limiter instance
            rate_limit_config: Rate limiting configuration
            **kwargs: Additional configuration
        """
        super().__init__()
        self.client = client
        
        # Cache configuration
        self.cache_config = cache_config
        self.cache_backend = cache_backend
        
        # Rate limiting configuration
        self.rate_limiter = rate_limiter
        self.rate_limit_config = rate_limit_config
        
        # Initialize cache backend if not provided
        if self.cache_config and not self.cache_backend:
            self.cache_backend = self._create_cache_backend()
        
        # Initialize rate limiter if not provided
        if self.rate_limit_config and not self.rate_limiter:
            self.rate_limiter = self._create_rate_limiter()
        
        logger.info(f"Initialized {self.__class__.__name__} with caching and rate limiting")
    
    def _create_cache_backend(self) -> Optional[CacheBackend]:
        """Create cache backend from configuration."""
        if not self.cache_config:
            return None
        
        try:
            from ..caching.backends import MemoryCache, RedisCache, FileCache
            
            backend_name = self.cache_config.backend
            backend_config = self.cache_config.to_backend_config()
            
            if backend_name == "memory":
                return MemoryCache(**backend_config)
            elif backend_name == "redis":
                return RedisCache(**backend_config)
            elif backend_name == "file":
                return FileCache(**backend_config)
            else:
                logger.warning(f"Unknown cache backend: {backend_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create cache backend: {e}")
            return None
    
    def _create_rate_limiter(self) -> Optional[RateLimiter]:
        """Create rate limiter from configuration."""
        if not self.rate_limit_config:
            return None
        
        try:
            from ..rate_limiting import RateLimiter
            return RateLimiter(config=self.rate_limit_config)
        except Exception as e:
            logger.error(f"Failed to create rate limiter: {e}")
            return None
    
    def _apply_rate_limiting(self, endpoint: str = "default") -> bool:
        """
        Apply rate limiting before making a request.
        
        Args:
            endpoint: Endpoint identifier
            
        Returns:
            True if request is allowed
        """
        if not self.rate_limiter:
            return True
        
        try:
            return self.rate_limiter.acquire(endpoint)
        except Exception as e:
            logger.warning(f"Rate limiting failed: {e}")
            return True  # Allow request if rate limiting fails
    
    async def _apply_rate_limiting_async(self, endpoint: str = "default") -> bool:
        """
        Apply rate limiting before making an async request.
        
        Args:
            endpoint: Endpoint identifier
            
        Returns:
            True if request is allowed
        """
        if not self.rate_limiter:
            return True
        
        try:
            return await self.rate_limiter.acquire_async(endpoint)
        except Exception as e:
            logger.warning(f"Rate limiting failed: {e}")
            return True  # Allow request if rate limiting fails
    
    def _record_request_success(self, endpoint: str = "default", response_time: float = 0.0):
        """Record a successful request."""
        if self.rate_limiter:
            self.rate_limiter.record_success(endpoint)
    
    def _record_request_error(self, endpoint: str = "default", error_code: Optional[int] = None):
        """Record a request error."""
        if self.rate_limiter:
            self.rate_limiter.record_error(endpoint, error_code)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache_backend:
            return {}
        
        try:
            return self.cache_backend.get_stats()
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {}
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        if not self.rate_limiter:
            return {}
        
        try:
            return self.rate_limiter.get_stats()
        except Exception as e:
            logger.warning(f"Failed to get rate limit stats: {e}")
            return {}
    
    def clear_cache(self) -> bool:
        """Clear the cache."""
        if not self.cache_backend:
            return False
        
        try:
            return self.cache_backend.clear()
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")
            return False
    
    def reset_rate_limiter(self, endpoint: Optional[str] = None):
        """Reset the rate limiter."""
        if self.rate_limiter:
            self.rate_limiter.reset(endpoint)


def with_caching(
    ttl: Optional[int] = None,
    endpoint: str = "default",
    skip_cache: bool = False
):
    """
    Decorator for adding caching to service methods.
    
    Args:
        ttl: Time to live in seconds
        endpoint: Endpoint identifier
        skip_cache: Skip caching for this method
    
    Example:
        @with_caching(ttl=3600)
        def get(self, congress: int, bill_type: str, bill_number: int):
            # Method implementation
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Check if this is a cached service
            if not hasattr(self, 'cache_backend') or not self.cache_backend:
                return func(self, *args, **kwargs)
            
            # Skip caching if disabled
            if skip_cache:
                return func(self, *args, **kwargs)
            
            # Apply rate limiting
            if not self._apply_rate_limiting(endpoint):
                # Rate limited - wait for availability
                wait_time = self.rate_limiter.wait_for_availability(endpoint)
                logger.debug(f"Rate limited, waited {wait_time:.2f}s")
            
            # Generate cache key
            from ..caching.keys import generate_cache_key
            service_name = self.__class__.__name__.lower().replace('cached', '')
            method_name = func.__name__
            cache_key = generate_cache_key(service_name, method_name, args, kwargs)
            
            # Try to get from cache
            try:
                cached_result = self.cache_backend.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {method_name}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")
            
            # Cache miss - call function
            start_time = time.time()
            try:
                result = func(self, *args, **kwargs)
                
                # Store in cache
                try:
                    effective_ttl = ttl or (self.cache_config.get_effective_ttl(
                        service_name, method_name, ttl
                    ) if self.cache_config else 3600)
                    self.cache_backend.set(cache_key, result, ttl=effective_ttl)
                    logger.debug(f"Cached result for {method_name}")
                except Exception as e:
                    logger.warning(f"Cache set failed: {e}")
                
                # Record success
                response_time = time.time() - start_time
                self._record_request_success(endpoint, response_time)
                
                return result
                
            except Exception:
                # Record error
                self._record_request_error(endpoint)
                raise
        
        return wrapper
    return decorator


def with_async_caching(
    ttl: Optional[int] = None,
    endpoint: str = "default",
    skip_cache: bool = False
):
    """
    Decorator for adding caching to async service methods.
    
    Args:
        ttl: Time to live in seconds
        endpoint: Endpoint identifier
        skip_cache: Skip caching for this method
    
    Example:
        @with_async_caching(ttl=3600)
        async def get(self, congress: int, bill_type: str, bill_number: int):
            # Async method implementation
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Check if this is a cached service
            if not hasattr(self, 'cache_backend') or not self.cache_backend:
                return await func(self, *args, **kwargs)
            
            # Skip caching if disabled
            if skip_cache:
                return await func(self, *args, **kwargs)
            
            # Apply rate limiting
            if not await self._apply_rate_limiting_async(endpoint):
                # Rate limited - wait for availability
                wait_time = await self.rate_limiter.wait_for_availability_async(endpoint)
                logger.debug(f"Rate limited, waited {wait_time:.2f}s")
            
            # Generate cache key
            from ..caching.keys import generate_cache_key
            service_name = self.__class__.__name__.lower().replace('cached', '')
            method_name = func.__name__
            cache_key = generate_cache_key(service_name, method_name, args, kwargs)
            
            # Try to get from cache
            try:
                cached_result = self.cache_backend.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {method_name}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")
            
            # Cache miss - call function
            start_time = time.time()
            try:
                result = await func(self, *args, **kwargs)
                
                # Store in cache
                try:
                    effective_ttl = ttl or (self.cache_config.get_effective_ttl(
                        service_name, method_name, ttl
                    ) if self.cache_config else 3600)
                    self.cache_backend.set(cache_key, result, ttl=effective_ttl)
                    logger.debug(f"Cached result for {method_name}")
                except Exception as e:
                    logger.warning(f"Cache set failed: {e}")
                
                # Record success
                response_time = time.time() - start_time
                self._record_request_success(endpoint, response_time)
                
                return result
                
            except Exception:
                # Record error
                self._record_request_error(endpoint)
                raise
        
        return wrapper
    return decorator
