"""Redis-backed cache with connection pooling, serialization, and TTL support."""

from __future__ import annotations

from typing import Any, Optional
import logging
import threading

from .base import BaseCacheBackend

logger = logging.getLogger(__name__)

# Redis is optional - only import if available
try:
    import redis
    from redis.connection import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    ConnectionPool = None


class RedisCache(BaseCacheBackend):
    """Redis-backed cache, shareable across processes/machines, with
    pooled connections and TTL via Redis EXPIRE.

    Example:
        cache = RedisCache(host="localhost", port=6379, db=0)
        cache.set("key", "value", ttl=60)
        value = cache.get("key")
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_connections: int = 10,
        default_ttl: Optional[int] = None,
        key_prefix: str = "congress_cache:",
        **kwargs
    ):
        """
        Initialize the Redis cache.
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            max_connections: Maximum connections in pool
            default_ttl: Default TTL in seconds
            key_prefix: Prefix for all cache keys
            **kwargs: Additional Redis configuration
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis is not available. Install with: pip install redis"
            )
        
        super().__init__(default_ttl=default_ttl, **kwargs)
        
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.key_prefix = key_prefix
        self._lock = threading.RLock()
        
        # Create connection pool
        self._pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            **kwargs
        )
        
        # Create Redis client
        self._client = redis.Redis(connection_pool=self._pool)
        
        # Test connection
        try:
            self._client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except redis.RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _make_key(self, key: str) -> str:
        """Add prefix to cache key."""
        return f"{self.key_prefix}{key}"
    
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
                redis_key = self._make_key(key)
                data = self._client.get(redis_key)
                
                if data is None:
                    self._record_miss()
                    return None
                
                # Deserialize the value
                value = self._deserialize_value(data.decode('utf-8'))
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
                redis_key = self._make_key(key)
                serialized_value = self._serialize_value(value)
                
                # Use provided TTL or default
                effective_ttl = ttl if ttl is not None else self.default_ttl
                
                # Store in Redis
                if effective_ttl is not None:
                    self._client.setex(redis_key, effective_ttl, serialized_value)
                else:
                    self._client.set(redis_key, serialized_value)
                
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
                redis_key = self._make_key(key)
                result = self._client.delete(redis_key)
                
                if result > 0:
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
                redis_key = self._make_key(key)
                return bool(self._client.exists(redis_key))
                
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
                # Get all keys with our prefix
                pattern = f"{self.key_prefix}*"
                keys = self._client.keys(pattern)
                
                if keys:
                    self._client.delete(*keys)
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            self._record_error()
            return False
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics including Redis info."""
        stats = super().get_stats()
        
        try:
            with self._lock:
                # Get Redis info
                info = self._client.info()
                
                stats.update({
                    'redis_version': info.get('redis_version'),
                    'used_memory': info.get('used_memory'),
                    'connected_clients': info.get('connected_clients'),
                    'total_commands_processed': info.get('total_commands_processed'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                })
                
                # Calculate Redis hit rate
                total_redis_requests = stats['keyspace_hits'] + stats['keyspace_misses']
                if total_redis_requests > 0:
                    stats['redis_hit_rate'] = stats['keyspace_hits'] / total_redis_requests
                else:
                    stats['redis_hit_rate'] = 0.0
                    
        except Exception as e:
            logger.warning(f"Failed to get Redis stats: {e}")
        
        return stats
    
    def close(self):
        """Close the Redis connection pool."""
        try:
            self._client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except Exception:
            pass







