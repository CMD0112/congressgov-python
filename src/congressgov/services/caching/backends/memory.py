"""Thread-safe in-memory cache (OrderedDict) with LRU eviction at capacity."""

from __future__ import annotations

from typing import Any, Optional
import threading
import time
from collections import OrderedDict
import logging

from .base import BaseCacheBackend, CacheEntry

logger = logging.getLogger(__name__)


class MemoryCache(BaseCacheBackend):
    """In-memory cache with O(1) operations, LRU eviction at capacity, and TTL expiration.

    Example:
        cache = MemoryCache(max_size=1000, default_ttl=300)
        cache.set("key", "value", ttl=60)
        value = cache.get("key")
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize the memory cache.
        
        Args:
            max_size: Maximum number of entries to store
            default_ttl: Default TTL in seconds
            **kwargs: Additional configuration (ignored)
        """
        super().__init__(default_ttl=default_ttl, **kwargs)
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()  # Reentrant lock for thread safety
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self._record_miss()
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self._record_miss()
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._record_hit()
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds (uses default if None)
            
        Returns:
            True if successful
        """
        try:
            with self._lock:
                # Use provided TTL or default
                effective_ttl = ttl if ttl is not None else self.default_ttl
                
                # Create cache entry
                entry = CacheEntry(
                    value=value,
                    timestamp=time.time(),
                    ttl=effective_ttl
                )
                
                # Store in cache
                self._cache[key] = entry
                
                # Evict if over capacity
                self._evict_if_needed()
                
                self._record_set()
                return True
                
        except Exception as e:
            logger.error(f"Failed to set cache key '{key}': {e}")
            self._record_error()
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._record_delete()
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if key exists and not expired, False otherwise
        """
        with self._lock:
            if key not in self._cache:
                return False
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                return False
            
            return True
    
    def clear(self) -> bool:
        """
        Clear all entries from the cache.
        
        Returns:
            True if successful
        """
        try:
            with self._lock:
                self._cache.clear()
                return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            self._record_error()
            return False
    
    def _evict_if_needed(self):
        """Evict least recently used entries if cache is over capacity."""
        while len(self._cache) > self.max_size:
            # Remove least recently used (first item)
            self._cache.popitem(last=False)
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics including memory usage."""
        stats = super().get_stats()
        with self._lock:
            stats.update({
                'size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage_ratio': len(self._cache) / self.max_size
            })
        return stats
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from the cache.
        
        Returns:
            Number of entries removed
        """
        removed = 0
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                removed += 1
        
        if removed > 0:
            logger.debug(f"Cleaned up {removed} expired entries")
        
        return removed







