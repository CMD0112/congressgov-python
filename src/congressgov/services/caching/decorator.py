"""Decorators that cache a service method's results with configurable TTL and backend."""

from __future__ import annotations

from typing import Any, Callable, Optional, Union
import functools
import logging
from inspect import iscoroutinefunction

from .config import CacheConfig
from .keys import generate_cache_key
from .backends.base import CacheBackend

logger = logging.getLogger(__name__)


def cacheable(
    ttl: Optional[int] = None,
    backend: Optional[Union[str, CacheBackend]] = None,
    key_func: Optional[Callable] = None,
    skip_cache: bool = False,
    cache_config: Optional[CacheConfig] = None
):
    """
    Decorator for caching synchronous method results.
    
    Args:
        ttl: Time to live in seconds (overrides cache config)
        backend: Cache backend to use (overrides cache config)
        key_func: Custom key generation function
        skip_cache: Skip caching for this method
        cache_config: Cache configuration (if None, uses instance config)
    
    Example:
        @cacheable(ttl=3600)
        def get(self, congress: int, bill_type: str, bill_number: int):
            # Method implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Skip caching if disabled
            if skip_cache:
                return func(self, *args, **kwargs)
            
            # Get cache configuration
            config = cache_config or getattr(self, 'cache_config', None)
            if config is None:
                # No caching configured, call function directly
                return func(self, *args, **kwargs)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(self, *args, **kwargs)
            else:
                service_name = self.__class__.__name__.lower().replace('async', '')
                method_name = func.__name__
                cache_key = generate_cache_key(service_name, method_name, args, kwargs)
            
            # Get cache backend
            cache_backend = _get_cache_backend(config, backend)
            if cache_backend is None:
                return func(self, *args, **kwargs)
            
            # Try to get from cache
            try:
                cached_result = cache_backend.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache get failed for key '{cache_key}': {e}")
            
            # Cache miss - call function
            logger.debug(f"Cache miss for key: {cache_key}")
            result = func(self, *args, **kwargs)
            
            # Store in cache
            try:
                effective_ttl = ttl or config.get_effective_ttl(
                    service_name, method_name, ttl
                )
                cache_backend.set(cache_key, result, ttl=effective_ttl)
                logger.debug(f"Cached result for key: {cache_key}")
            except Exception as e:
                logger.warning(f"Cache set failed for key '{cache_key}': {e}")
            
            return result
        
        return wrapper
    return decorator


def async_cacheable(
    ttl: Optional[int] = None,
    backend: Optional[Union[str, CacheBackend]] = None,
    key_func: Optional[Callable] = None,
    skip_cache: bool = False,
    cache_config: Optional[CacheConfig] = None
):
    """
    Decorator for caching asynchronous method results.
    
    Args:
        ttl: Time to live in seconds (overrides cache config)
        backend: Cache backend to use (overrides cache config)
        key_func: Custom key generation function
        skip_cache: Skip caching for this method
        cache_config: Cache configuration (if None, uses instance config)
    
    Example:
        @async_cacheable(ttl=3600)
        async def get(self, congress: int, bill_type: str, bill_number: int):
            # Async method implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Skip caching if disabled
            if skip_cache:
                return await func(self, *args, **kwargs)
            
            # Get cache configuration
            config = cache_config or getattr(self, 'cache_config', None)
            if config is None:
                # No caching configured, call function directly
                return await func(self, *args, **kwargs)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(self, *args, **kwargs)
            else:
                service_name = self.__class__.__name__.lower().replace('async', '')
                method_name = func.__name__
                cache_key = generate_cache_key(service_name, method_name, args, kwargs)
            
            # Get cache backend
            cache_backend = _get_cache_backend(config, backend)
            if cache_backend is None:
                return await func(self, *args, **kwargs)
            
            # Try to get from cache
            try:
                cached_result = cache_backend.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache get failed for key '{cache_key}': {e}")
            
            # Cache miss - call function
            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(self, *args, **kwargs)
            
            # Store in cache
            try:
                effective_ttl = ttl or config.get_effective_ttl(
                    service_name, method_name, ttl
                )
                cache_backend.set(cache_key, result, ttl=effective_ttl)
                logger.debug(f"Cached result for key: {cache_key}")
            except Exception as e:
                logger.warning(f"Cache set failed for key '{cache_key}': {e}")
            
            return result
        
        return wrapper
    return decorator


def _get_cache_backend(
    config: CacheConfig,
    backend: Optional[Union[str, CacheBackend]] = None
) -> Optional[CacheBackend]:
    """
    Get cache backend from configuration.
    
    Args:
        config: Cache configuration
        backend: Override backend
        
    Returns:
        Cache backend instance or None
    """
    try:
        # Use provided backend or config backend
        backend_name = backend or config.backend
        
        if isinstance(backend_name, CacheBackend):
            return backend_name
        
        # Create backend based on name
        if backend_name == "memory":
            from .backends.memory import MemoryCache
            return MemoryCache(**config.to_backend_config())
        elif backend_name == "redis":
            from .backends.redis import RedisCache
            return RedisCache(**config.to_backend_config())
        elif backend_name == "file":
            from .backends.file import FileCache
            return FileCache(**config.to_backend_config())
        else:
            logger.warning(f"Unknown cache backend: {backend_name}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to create cache backend: {e}")
        return None


def cache_invalidate(
    patterns: Optional[list[str]] = None,
    service_name: Optional[str] = None
):
    """
    Decorator for methods that should invalidate cache entries.
    
    Args:
        patterns: Cache key patterns to invalidate
        service_name: Service name for pattern generation
    
    Example:
        @cache_invalidate(patterns=["bill:*"])
        def update_bill(self, bill_id: str):
            # Method that updates bill data
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            
            # Invalidate cache patterns
            if patterns:
                _invalidate_patterns(self, patterns, service_name)
            
            return result
        
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            result = await func(self, *args, **kwargs)
            
            # Invalidate cache patterns
            if patterns:
                _invalidate_patterns(self, patterns, service_name)
            
            return result
        
        # Return appropriate wrapper based on function type
        if iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator


def _invalidate_patterns(
    instance: Any,
    patterns: list[str],
    service_name: Optional[str] = None
):
    """
    Invalidate cache patterns.
    
    Args:
        instance: Service instance
        patterns: Patterns to invalidate
        service_name: Service name for pattern generation
    """
    try:
        config = getattr(instance, 'cache_config', None)
        if config is None:
            return
        
        cache_backend = _get_cache_backend(config)
        if cache_backend is None:
            return
        
        # Generate full patterns
        if service_name:
            from .keys import generate_pattern_key
            full_patterns = [
                generate_pattern_key(service_name, "*", pattern)
                for pattern in patterns
            ]
        else:
            full_patterns = patterns
        
        # Invalidate each pattern
        for pattern in full_patterns:
            try:
                if hasattr(cache_backend, 'delete_pattern'):
                    cache_backend.delete_pattern(pattern)
                else:
                    # Fallback: clear all if pattern deletion not supported
                    cache_backend.clear()
                logger.debug(f"Invalidated cache pattern: {pattern}")
            except Exception as e:
                logger.warning(f"Failed to invalidate pattern '{pattern}': {e}")
                
    except Exception as e:
        logger.error(f"Cache invalidation failed: {e}")


# Convenience decorators for common use cases
def cache_bill(ttl: int = 3600):
    """Cache decorator optimized for bill data."""
    return cacheable(ttl=ttl)


def cache_member(ttl: int = 1800):
    """Cache decorator optimized for member data."""
    return cacheable(ttl=ttl)


def cache_committee(ttl: int = 7200):
    """Cache decorator optimized for committee data."""
    return cacheable(ttl=ttl)


def cache_search(ttl: int = 300):
    """Cache decorator optimized for search results."""
    return cacheable(ttl=ttl)


# Async versions
def async_cache_bill(ttl: int = 3600):
    """Async cache decorator optimized for bill data."""
    return async_cacheable(ttl=ttl)


def async_cache_member(ttl: int = 1800):
    """Async cache decorator optimized for member data."""
    return async_cacheable(ttl=ttl)


def async_cache_committee(ttl: int = 7200):
    """Async cache decorator optimized for committee data."""
    return async_cacheable(ttl=ttl)


def async_cache_search(ttl: int = 300):
    """Async cache decorator optimized for search results."""
    return async_cacheable(ttl=ttl)







