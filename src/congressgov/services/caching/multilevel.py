"""
Multi-level cache implementation with cascading lookups.

This module provides a multi-level cache that checks multiple cache
backends in order, providing a hierarchy of speed vs. capacity.
"""

from __future__ import annotations

from typing import Any, List, Optional, Dict
import logging
import time

from .backends.base import CacheBackend, BaseCacheBackend

logger = logging.getLogger(__name__)


class MultiLevelCache(BaseCacheBackend):
    """
    Multi-level cache with cascading lookups.

    .. deprecated::
        Use the request store blob lane via ``get_client_from_env()`` instead.

    Features:
    - Cascading lookups (L1 -> L2 -> L3 -> ...)
    - Write-through to all levels
    - Automatic promotion of hot data to faster levels
    - Configurable TTL per level
    - Fallback handling
    """
    
    def __init__(
        self,
        backends: List[CacheBackend],
        write_through: bool = True,
        promote_hot_data: bool = True,
        **kwargs
    ):
        """
        Initialize multi-level cache.
        
        Args:
            backends: List of cache backends (ordered by speed)
            write_through: Write to all levels on set
            promote_hot_data: Move frequently accessed data to faster levels
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        
        if not backends:
            raise ValueError("At least one cache backend is required")
        
        self.backends = backends
        self.write_through = write_through
        self.promote_hot_data = promote_hot_data
        
        # Track access patterns for hot data promotion
        self._access_counts: Dict[str, int] = {}
        self._last_access: Dict[str, float] = {}
        
        logger.info(f"Initialized multi-level cache with {len(backends)} levels")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value using cascading lookup.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found in any level
        """
        # Track access for hot data promotion
        if self.promote_hot_data:
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            self._last_access[key] = time.time()
        
        # Try each backend in order
        for i, backend in enumerate(self.backends):
            try:
                value = backend.get(key)
                if value is not None:
                    # Cache hit - promote to faster levels if enabled
                    if self.promote_hot_data and i > 0:
                        self._promote_to_faster_levels(key, value, i)
                    
                    self._record_hit()
                    logger.debug(f"Cache hit at level {i} for key: {key}")
                    return value
                    
            except Exception as e:
                logger.warning(f"Cache get failed at level {i} for key '{key}': {e}")
                continue
        
        # Cache miss at all levels
        self._record_miss()
        logger.debug(f"Cache miss at all levels for key: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful at any level
        """
        success = False
        
        if self.write_through:
            # Write to all levels
            for i, backend in enumerate(self.backends):
                try:
                    # Use different TTL for different levels if not specified
                    level_ttl = ttl or self._get_level_ttl(i)
                    if backend.set(key, value, ttl=level_ttl):
                        success = True
                        logger.debug(f"Set cache at level {i} for key: {key}")
                except Exception as e:
                    logger.warning(f"Cache set failed at level {i} for key '{key}': {e}")
                    continue
        else:
            # Write to first level only
            try:
                if self.backends[0].set(key, value, ttl=ttl):
                    success = True
                    logger.debug(f"Set cache at level 0 for key: {key}")
            except Exception as e:
                logger.warning(f"Cache set failed at level 0 for key '{key}': {e}")
        
        if success:
            self._record_set()
        
        return success
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from all cache levels.
        
        Args:
            key: The cache key
            
        Returns:
            True if deleted from any level
        """
        success = False
        
        for i, backend in enumerate(self.backends):
            try:
                if backend.delete(key):
                    success = True
                    logger.debug(f"Deleted cache at level {i} for key: {key}")
            except Exception as e:
                logger.warning(f"Cache delete failed at level {i} for key '{key}': {e}")
                continue
        
        if success:
            self._record_delete()
        
        return success
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in any cache level.
        
        Args:
            key: The cache key
            
        Returns:
            True if key exists in any level
        """
        for i, backend in enumerate(self.backends):
            try:
                if backend.exists(key):
                    return True
            except Exception as e:
                logger.warning(f"Cache exists check failed at level {i} for key '{key}': {e}")
                continue
        
        return False
    
    def clear(self) -> bool:
        """
        Clear all cache levels.
        
        Returns:
            True if all levels cleared successfully
        """
        success = True
        
        for i, backend in enumerate(self.backends):
            try:
                if not backend.clear():
                    success = False
                    logger.warning(f"Cache clear failed at level {i}")
            except Exception as e:
                logger.warning(f"Cache clear failed at level {i}: {e}")
                success = False
        
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all cache levels."""
        stats = super().get_stats()
        
        # Add per-level statistics
        level_stats = []
        for i, backend in enumerate(self.backends):
            try:
                level_stat = backend.get_stats()
                level_stat['level'] = i
                level_stats.append(level_stat)
            except Exception as e:
                logger.warning(f"Failed to get stats for level {i}: {e}")
                level_stats.append({'level': i, 'error': str(e)})
        
        stats['levels'] = level_stats
        stats['num_levels'] = len(self.backends)
        
        # Add hot data statistics
        if self.promote_hot_data:
            stats['hot_data'] = {
                'total_keys': len(self._access_counts),
                'most_accessed': self._get_most_accessed_keys(10),
                'recently_accessed': self._get_recently_accessed_keys(10)
            }
        
        return stats
    
    def _get_level_ttl(self, level: int) -> Optional[int]:
        """
        Get TTL for a specific level.
        
        Args:
            level: Cache level (0-based)
            
        Returns:
            TTL in seconds
        """
        # Default TTL increases with level (faster levels have shorter TTL)
        default_ttls = [300, 3600, 86400]  # 5min, 1hr, 24hr
        return default_ttls[min(level, len(default_ttls) - 1)]
    
    def _promote_to_faster_levels(self, key: str, value: Any, found_level: int):
        """
        Promote frequently accessed data to faster cache levels.
        
        Args:
            key: The cache key
            value: The cached value
            found_level: Level where the value was found
        """
        if not self.promote_hot_data:
            return
        
        # Check if this key is "hot" (accessed frequently)
        access_count = self._access_counts.get(key, 0)
        if access_count < 3:  # Threshold for hot data
            return
        
        # Promote to faster levels
        for i in range(found_level):
            try:
                level_ttl = self._get_level_ttl(i)
                self.backends[i].set(key, value, ttl=level_ttl)
                logger.debug(f"Promoted key '{key}' to level {i}")
            except Exception as e:
                logger.warning(f"Failed to promote key '{key}' to level {i}: {e}")
    
    def _get_most_accessed_keys(self, limit: int = 10) -> List[tuple[str, int]]:
        """Get most frequently accessed keys."""
        return sorted(
            self._access_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
    
    def _get_recently_accessed_keys(self, limit: int = 10) -> List[tuple[str, float]]:
        """Get most recently accessed keys."""
        return sorted(
            self._last_access.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
    
    def cleanup_hot_data_tracking(self, max_age: int = 3600):
        """
        Clean up old hot data tracking information.
        
        Args:
            max_age: Maximum age in seconds for tracking data
        """
        current_time = time.time()
        cutoff_time = current_time - max_age
        
        # Remove old access tracking
        old_keys = [
            key for key, last_access in self._last_access.items()
            if last_access < cutoff_time
        ]
        
        for key in old_keys:
            self._access_counts.pop(key, None)
            self._last_access.pop(key, None)
        
        if old_keys:
            logger.debug(f"Cleaned up hot data tracking for {len(old_keys)} keys")
    
    def warm_cache(self, keys_and_values: List[tuple[str, Any]]):
        """
        Warm the cache with pre-computed data.
        
        Args:
            keys_and_values: List of (key, value) tuples to cache
        """
        for key, value in keys_and_values:
            self.set(key, value)
        
        logger.info(f"Warmed cache with {len(keys_and_values)} entries")







