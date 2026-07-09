"""
Base cache backend protocol and interfaces.

This module defines the CacheBackend protocol that all cache implementations
must follow, ensuring consistent behavior across different storage backends.
"""

from __future__ import annotations

from typing import Any, Optional, Protocol
import time
import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class CacheBackend(Protocol):
    """
    Protocol defining the interface for all cache backends.
    
    All cache backends must implement these methods to ensure
    consistent behavior across different storage mechanisms.
    """
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found/expired
        """
        ...
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds (None for no expiration)
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if deleted, False if not found
        """
        ...
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if key exists and not expired, False otherwise
        """
        ...
    
    def clear(self) -> bool:
        """
        Clear all entries from the cache.
        
        Returns:
            True if successful, False otherwise
        """
        ...
    
    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        ...


class BaseCacheBackend(ABC):
    """
    Abstract base class for cache backends with common functionality.
    
    Provides serialization, TTL handling, and error management that
    can be shared across different backend implementations.
    """
    
    def __init__(
        self,
        default_ttl: Optional[int] = None,
        serialize_func: Optional[callable] = None,
        deserialize_func: Optional[callable] = None,
        **kwargs
    ):
        """
        Initialize the cache backend.
        
        Args:
            default_ttl: Default TTL in seconds for entries
            serialize_func: Function to serialize values (default: json.dumps)
            deserialize_func: Function to deserialize values (default: json.loads)
            **kwargs: Additional backend-specific configuration
        """
        self.default_ttl = default_ttl
        self.serialize_func = serialize_func or self._default_serialize
        self.deserialize_func = deserialize_func or self._default_deserialize
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
    
    def _default_serialize(self, value: Any) -> str:
        """Default serialization using JSON."""
        try:
            return json.dumps(value, default=str)
        except (TypeError, ValueError) as e:
            logger.warning(f"Serialization failed: {e}")
            return json.dumps(str(value))
    
    def _default_deserialize(self, data: str) -> Any:
        """Default deserialization using JSON."""
        try:
            return json.loads(data)
        except (TypeError, ValueError) as e:
            logger.warning(f"Deserialization failed: {e}")
            return data
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize a value for storage."""
        return self.serialize_func(value)
    
    def _deserialize_value(self, data: str) -> Any:
        """Deserialize a value from storage."""
        return self.deserialize_func(data)
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Check if an entry has expired."""
        return time.time() - timestamp > ttl
    
    def _record_hit(self):
        """Record a cache hit."""
        self._stats['hits'] += 1
    
    def _record_miss(self):
        """Record a cache miss."""
        self._stats['misses'] += 1
    
    def _record_set(self):
        """Record a cache set operation."""
        self._stats['sets'] += 1
    
    def _record_delete(self):
        """Record a cache delete operation."""
        self._stats['deletes'] += 1
    
    def _record_error(self):
        """Record a cache error."""
        self._stats['errors'] += 1
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        stats = self._stats.copy()
        total_requests = stats['hits'] + stats['misses']
        stats['hit_rate'] = stats['hits'] / total_requests if total_requests > 0 else 0.0
        return stats
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store a value in the cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all entries from the cache."""
        pass


class CacheEntry:
    """
    Represents a cached entry with metadata.
    
    Used internally by cache backends to store values along with
    timestamps and TTL information.
    """
    
    def __init__(self, value: Any, timestamp: float, ttl: Optional[int] = None):
        """
        Initialize a cache entry.
        
        Args:
            value: The cached value
            timestamp: When the entry was created
            ttl: Time to live in seconds
        """
        self.value = value
        self.timestamp = timestamp
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'value': self.value,
            'timestamp': self.timestamp,
            'ttl': self.ttl
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary."""
        return cls(
            value=data['value'],
            timestamp=data['timestamp'],
            ttl=data.get('ttl')
        )







