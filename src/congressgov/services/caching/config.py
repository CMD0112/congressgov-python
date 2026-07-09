"""
Cache configuration and TTL strategies.

This module provides configuration classes for the caching system,
including TTL strategies and cache backend configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union

if TYPE_CHECKING:
    from .backends.base import CacheBackend
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TTLStrategy(Enum):
    """TTL (Time To Live) strategies for cache entries."""
    
    STATIC = "static"  # Fixed TTL for all entries
    DYNAMIC = "dynamic"  # TTL based on data type or endpoint
    ADAPTIVE = "adaptive"  # TTL based on access patterns


@dataclass
class CacheConfig:
    """
    Configuration for cache backends and behavior.
    
    This class provides a unified way to configure caching across
    different backends and use cases.
    """
    
    # Backend configuration
    backend: Union[str, CacheBackend] = "memory"
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    path: Union[str, None] = "./cache"
    
    # Cache behavior
    default_ttl: Optional[int] = 3600  # 1 hour default
    max_size: int = 10000
    key_prefix: str = "congress_cache:"
    
    # TTL strategy
    ttl_strategy: TTLStrategy = TTLStrategy.DYNAMIC
    
    # Per-endpoint TTL configuration
    endpoint_ttls: Dict[str, int] = field(default_factory=lambda: {
        "bill": 3600,      # 1 hour - bills change infrequently
        "member": 1800,    # 30 minutes - member data changes more often
        "committee": 7200, # 2 hours - committee data is very stable
        "amendment": 1800, # 30 minutes - amendments change frequently
        "search": 300,     # 5 minutes - search results change often
    })
    
    # Serialization
    serialize_func: Optional[Callable[[Any], str]] = None
    deserialize_func: Optional[Callable[[str], Any]] = None
    
    # Advanced options
    enable_compression: bool = False
    compression_threshold: int = 1024  # Compress if > 1KB
    enable_analytics: bool = True
    
    def get_ttl_for_endpoint(self, endpoint: str) -> int:
        """
        Get TTL for a specific endpoint.
        
        Args:
            endpoint: The endpoint name (e.g., 'bill', 'member')
            
        Returns:
            TTL in seconds
        """
        if self.ttl_strategy == TTLStrategy.STATIC:
            return self.default_ttl or 3600
        
        return self.endpoint_ttls.get(endpoint, self.default_ttl or 3600)
    
    def get_ttl_for_method(self, method_name: str) -> int:
        """
        Get TTL for a specific method.
        
        Args:
            method_name: The method name (e.g., 'get', 'search')
            
        Returns:
            TTL in seconds
        """
        # Different TTLs for different operations
        method_ttls = {
            "get": 3600,      # Individual items cached longer
            "search": 300,    # Search results cached shorter
            "list": 600,      # List operations medium TTL
        }
        
        if self.ttl_strategy == TTLStrategy.STATIC:
            return self.default_ttl or 3600
        
        return method_ttls.get(method_name, self.default_ttl or 3600)
    
    def get_effective_ttl(self, endpoint: str, method: str, custom_ttl: Optional[int] = None) -> int:
        """
        Get the effective TTL for a cache entry.
        
        Args:
            endpoint: The endpoint name
            method: The method name
            custom_ttl: Custom TTL override
            
        Returns:
            Effective TTL in seconds
        """
        if custom_ttl is not None:
            return custom_ttl
        
        if self.ttl_strategy == TTLStrategy.ADAPTIVE:
            # For adaptive strategy, use a base TTL and let the system adjust
            base_ttl = self.get_ttl_for_endpoint(endpoint)
            return min(base_ttl, self.get_ttl_for_method(method))
        
        # Use endpoint TTL as primary, method TTL as secondary
        endpoint_ttl = self.get_ttl_for_endpoint(endpoint)
        method_ttl = self.get_ttl_for_method(method)
        
        return min(endpoint_ttl, method_ttl)
    
    def to_backend_config(self) -> Dict[str, Any]:
        """
        Convert to backend-specific configuration.
        
        Returns:
            Dictionary of backend configuration
        """
        config = {
            "default_ttl": self.default_ttl,
            "serialize_func": self.serialize_func,
            "deserialize_func": self.deserialize_func,
        }
        
        if isinstance(self.backend, str):
            if self.backend == "redis":
                config.update({
                    "host": self.host,
                    "port": self.port,
                    "db": self.db,
                    "password": self.password,
                    "key_prefix": self.key_prefix,
                })
            elif self.backend == "file":
                config.update({
                    "path": self.path,
                    "max_size": self.max_size,
                })
            elif self.backend == "memory":
                config.update({
                    "max_size": self.max_size,
                })
        
        return config


@dataclass
class RateLimitConfig:
    """
    Configuration for rate limiting.
    
    This class provides configuration for rate limiting behavior
    to prevent hitting API rate limits.
    """
    
    # Rate limiting parameters
    requests_per_second: float = 10.0
    burst_size: int = 50
    backoff_factor: float = 2.0
    max_retries: int = 3
    
    # Retry configuration
    retry_on_status: tuple = (429, 503, 502, 504)  # HTTP status codes to retry
    initial_delay: float = 1.0
    max_delay: float = 60.0
    
    # Monitoring
    enable_monitoring: bool = True
    alert_threshold: float = 0.8  # Alert when 80% of rate limit used
    
    def get_delay_for_attempt(self, attempt: int) -> float:
        """
        Calculate delay for a retry attempt.
        
        Args:
            attempt: The attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        if attempt <= 0:
            return self.initial_delay
        
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)


@dataclass
class CacheInvalidationConfig:
    """
    Configuration for cache invalidation strategies.
    
    This class defines how and when cache entries should be invalidated.
    """
    
    # Invalidation rules
    invalidation_rules: Dict[str, list[str]] = field(default_factory=lambda: {
        "bill": ["bill:*", "bill_actions:*", "bill_cosponsors:*", "bill_summaries:*"],
        "member": ["member:*", "member_bills:*", "member_committees:*"],
        "committee": ["committee:*", "committee_bills:*", "committee_members:*"],
    })
    
    # Time-based invalidation
    enable_time_based: bool = True
    max_age: int = 86400  # 24 hours max age
    
    # Event-based invalidation
    enable_event_based: bool = True
    
    # Pattern-based invalidation
    enable_pattern_based: bool = True
    
    def get_invalidation_patterns(self, entity_type: str) -> list[str]:
        """
        Get invalidation patterns for an entity type.
        
        Args:
            entity_type: The type of entity (e.g., 'bill', 'member')
            
        Returns:
            List of invalidation patterns
        """
        return self.invalidation_rules.get(entity_type, [f"{entity_type}:*"])


# Predefined configurations for common use cases
def get_development_config() -> CacheConfig:
    """Get configuration optimized for development."""
    return CacheConfig(
        backend="memory",
        default_ttl=300,  # 5 minutes
        max_size=1000,
        enable_analytics=True,
    )


def get_production_config() -> CacheConfig:
    """Get configuration optimized for production."""
    return CacheConfig(
        backend="redis",
        host="localhost",
        port=6379,
        default_ttl=3600,  # 1 hour
        max_size=100000,
        enable_compression=True,
        enable_analytics=True,
    )


def get_offline_config() -> CacheConfig:
    """Get configuration for offline mode."""
    return CacheConfig(
        backend="file",
        path="./offline_cache",
        default_ttl=86400,  # 24 hours
        max_size=1000000,
        enable_compression=True,
    )







