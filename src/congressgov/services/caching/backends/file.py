"""File-based cache backend (via diskcache) that survives application restarts."""

from __future__ import annotations

from typing import Any, Optional, Union
import logging
import threading
from pathlib import Path

from .base import BaseCacheBackend

logger = logging.getLogger(__name__)

# diskcache is optional - only required when constructing FileCache
try:
    import diskcache  # noqa: F401

    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False


class FileCache(BaseCacheBackend):
    """Disk-backed cache: persistent across restarts, thread-safe, with
    automatic cleanup of expired entries.

    Example:
        cache = FileCache(path="./cache", max_size=10000)
        cache.set("key", "value", ttl=60)
        value = cache.get("key")
    """
    
    def __init__(
        self,
        path: Union[str, Path] = "./cache",
        max_size: int = 10000,
        default_ttl: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize the file cache.
        
        Args:
            path: Directory path for cache storage
            max_size: Maximum number of entries to store
            default_ttl: Default TTL in seconds
            **kwargs: Additional diskcache configuration
        """
        if not DISKCACHE_AVAILABLE:
            raise ImportError(
                "diskcache is not available. Install with: pip install diskcache"
            )
        
        super().__init__(default_ttl=default_ttl, **kwargs)
        
        self.path = Path(path)
        self.max_size = max_size
        self._lock = threading.RLock()
        
        # Create cache directory if it doesn't exist
        self.path.mkdir(parents=True, exist_ok=True)
        
        # Initialize diskcache (import here so type checkers see a real module)
        import diskcache as dc

        try:
            self._cache = dc.Cache(
                directory=str(self.path),
                size_limit=max_size,
                **kwargs
            )
            logger.info(f"File cache initialized at {self.path}")
        except Exception as e:
            logger.error(f"Failed to initialize file cache: {e}")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found/expired
        """
        try:
            with self._lock:
                if key not in self._cache:
                    self._record_miss()
                    return None
                
                # diskcache handles TTL automatically
                value = self._cache.get(key)
                
                if value is None:
                    # Key expired or doesn't exist
                    self._record_miss()
                    return None
                
                self._record_hit()
                return value
                
        except Exception as e:
            logger.error(f"Failed to get cache key '{key}': {e}")
            self._record_error()
            return None
    
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
                
                # Store in diskcache
                if effective_ttl is not None:
                    self._cache.set(key, value, expire=effective_ttl)
                else:
                    self._cache.set(key, value)
                
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
        try:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    self._record_delete()
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete cache key '{key}': {e}")
            self._record_error()
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if key exists and not expired, False otherwise
        """
        try:
            with self._lock:
                return key in self._cache
                
        except Exception as e:
            logger.error(f"Failed to check existence of key '{key}': {e}")
            self._record_error()
            return False
    
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
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics including disk usage."""
        stats = super().get_stats()
        
        try:
            with self._lock:
                # Some versions of diskcache Cache.__len__ may not return int as expected for type-checkers;
                # so use .count() which always returns int.
                stats.update({
                    'size': self._cache.count(),
                    'max_size': self.max_size,
                    'disk_usage': self._cache.volume(),
                    'cache_path': str(self.path),
                })
       
                
        except Exception as e:
            logger.warning(f"Failed to get file cache stats: {e}")
        
        return stats
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired entries (diskcache handles this automatically).
        
        Returns:
            Number of entries cleaned up
        """
        # diskcache automatically handles expiration
        # This method is here for interface compatibility
        return 0
    
    def close(self):
        """Close the file cache."""
        try:
            with self._lock:
                self._cache.close()
                logger.info("File cache closed")
        except Exception as e:
            logger.error(f"Error closing file cache: {e}")
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except Exception:
            pass







