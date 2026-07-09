"""Cache backends: `MemoryCache` (LRU, in-process), `RedisCache` (distributed),
and `FileCache` (persistent to disk), all implementing the `CacheBackend` protocol.
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







