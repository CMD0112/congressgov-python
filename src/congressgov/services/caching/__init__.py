"""
Caching layer for congressgov: memory/Redis/file backends, multi-level
cascading lookups, cache-key generation, invalidation rules, and analytics.

Usage:
    # Basic caching
    from congressgov.services.caching import CacheConfig, RedisBackend
    from congressgov import Bill
    
    cache_config = CacheConfig(
        backend=RedisBackend(host="localhost"),
        ttl=3600
    )
    
    bill_service = Bill(client=client, cache_config=cache_config)
    bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)  # Cached!
    
    # Multi-level caching
    from congressgov.services.caching import MultiLevelCache, MemoryCache, RedisCache
    
    cache = MultiLevelCache([
        MemoryCache(max_size=1000, ttl=300),
        RedisCache(host="localhost", ttl=3600)
    ])
    
    bill_service = Bill(client=client, cache=cache)
"""

# Core configuration and interfaces
from .config import CacheConfig, TTLStrategy
from .keys import CacheKeyGenerator

# Cache backends
from .backends.base import CacheBackend
from .backends.memory import MemoryCache
from .backends.redis import RedisCache
from .backends.file import FileCache

# Multi-level caching
from .multilevel import MultiLevelCache

# Decorators
from .decorator import cacheable, async_cacheable

# Cache management
from .invalidation import CacheInvalidator
from .analytics import CacheAnalytics

# Optional features
try:
    from .warming import CacheWarmer
    from .offline import OfflineMode
    from .compression import CacheCompressor
except ImportError:
    # Optional features not available
    pass

__all__ = [
    # Core
    'CacheConfig',
    'TTLStrategy',
    'CacheKeyGenerator',
    
    # Backends
    'CacheBackend',
    'MemoryCache',
    'RedisCache',
    'FileCache',
    
    # Multi-level
    'MultiLevelCache',
    
    # Decorators
    'cacheable',
    'async_cacheable',
    
    # Management
    'CacheInvalidator',
    'CacheAnalytics',
    
    # Optional features (if available)
    'CacheWarmer',
    'OfflineMode',
    'CacheCompressor',
]







