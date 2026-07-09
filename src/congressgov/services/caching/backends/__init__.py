"""
Cache backends for the congressgov caching system.

This module provides various cache backend implementations:
- MemoryCache: Fast in-memory caching with LRU eviction
- RedisCache: Distributed caching using Redis
- FileCache: Persistent file-based caching

All backends implement the CacheBackend protocol for consistent interface.
"""

from .base import CacheBackend
from .memory import MemoryCache
from .redis import RedisCache
from .file import FileCache

__all__ = [
    'CacheBackend',
    'MemoryCache', 
    'RedisCache',
    'FileCache',
]







