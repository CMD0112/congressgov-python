"""
Cache key generation and management.

This module provides utilities for generating consistent, deterministic
cache keys from method parameters and context.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import hashlib
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CacheKeyGenerator:
    """
    Generates consistent cache keys from method parameters.
    
    This class provides deterministic key generation that ensures
    the same parameters always produce the same cache key.
    """
    
    version: str = "v1"
    separator: str = ":"
    max_key_length: int = 250  # Redis key length limit
    
    def generate_key(
        self,
        service_name: str,
        method_name: str,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        prefix: str = "congress_cache"
    ) -> str:
        """
        Generate a cache key from method parameters.
        
        Args:
            service_name: Name of the service (e.g., 'bill', 'member')
            method_name: Name of the method (e.g., 'get', 'search')
            args: Positional arguments
            kwargs: Keyword arguments
            prefix: Key prefix
            
        Returns:
            Generated cache key
            
        Example:
            generator = CacheKeyGenerator()
            key = generator.generate_key(
                "bill", "get", 
                args=(118, "hr", 1),
                kwargs={"format_": "json"}
            )
            # Returns: "congress_cache:v1:bill:get:118:hr:1:format_=json"
        """
        if kwargs is None:
            kwargs = {}
        
        # Build key components
        components = [prefix, self.version, service_name, method_name]
        
        # Add positional arguments
        for arg in args:
            components.append(self._serialize_value(arg))
        
        # Add keyword arguments (sorted for consistency)
        for key, value in sorted(kwargs.items()):
            if value is not None:  # Skip None values
                components.append(f"{key}={self._serialize_value(value)}")
        
        # Join components
        key = self.separator.join(components)
        
        # Truncate if too long
        if len(key) > self.max_key_length:
            # Use hash for long keys
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{prefix}:{self.version}:{service_name}:{method_name}:hash:{key_hash}"
        
        return key
    
    def _serialize_value(self, value: Any) -> str:
        """
        Serialize a value for use in cache key.
        
        Args:
            value: The value to serialize
            
        Returns:
            String representation of the value
        """
        if value is None:
            return "None"
        elif isinstance(value, (str, int, float, bool)):
            return str(value)
        elif isinstance(value, (list, tuple)):
            # Sort lists/tuples for consistency
            sorted_items = sorted(value) if isinstance(value, list) else sorted(value)
            return f"[{','.join(self._serialize_value(item) for item in sorted_items)}]"
        elif isinstance(value, dict):
            # Sort dict items for consistency
            sorted_items = sorted(value.items())
            dict_items = [f"{k}={self._serialize_value(v)}" for k, v in sorted_items]
            return "{" + ",".join(dict_items) + "}"
        else:
            # For complex objects, use JSON serialization
            try:
                return json.dumps(value, default=str, sort_keys=True)
            except (TypeError, ValueError):
                return str(value)
    
    def generate_pattern_key(
        self,
        service_name: str,
        method_name: str,
        pattern: str = "*"
    ) -> str:
        """
        Generate a pattern key for cache invalidation.
        
        Args:
            service_name: Name of the service
            method_name: Name of the method
            pattern: Pattern to match (e.g., "*", "118:*")
            
        Returns:
            Pattern key for invalidation
            
        Example:
            generator.generate_pattern_key("bill", "get", "118:*")
            # Returns: "congress_cache:v1:bill:get:118:*"
        """
        components = ["congress_cache", self.version, service_name, method_name, pattern]
        return self.separator.join(components)
    
    def extract_parameters_from_key(self, key: str) -> Dict[str, Any]:
        """
        Extract parameters from a cache key (reverse of generate_key).
        
        Args:
            key: The cache key
            
        Returns:
            Dictionary with extracted parameters
        """
        try:
            parts = key.split(self.separator)
            
            if len(parts) < 4:
                return {}
            
            # Skip prefix and version
            service_name = parts[2]
            method_name = parts[3]
            
            result = {
                "service_name": service_name,
                "method_name": method_name,
                "args": [],
                "kwargs": {}
            }
            
            # Parse remaining parts
            for part in parts[4:]:
                if "=" in part:
                    # Keyword argument
                    key_part, value_part = part.split("=", 1)
                    result["kwargs"][key_part] = self._deserialize_value(value_part)
                else:
                    # Positional argument
                    result["args"].append(self._deserialize_value(part))
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to extract parameters from key '{key}': {e}")
            return {}
    
    def _deserialize_value(self, value_str: str) -> Any:
        """
        Deserialize a value from cache key string.
        
        Args:
            value_str: The string representation
            
        Returns:
            Deserialized value
        """
        if value_str == "None":
            return None
        elif value_str.lower() in ("true", "false"):
            return value_str.lower() == "true"
        elif value_str.isdigit():
            return int(value_str)
        elif value_str.replace(".", "").isdigit():
            return float(value_str)
        elif value_str.startswith("[") and value_str.endswith("]"):
            # List/tuple
            inner = value_str[1:-1]
            if not inner:
                return []
            return [self._deserialize_value(item) for item in inner.split(",")]
        elif value_str.startswith("{") and value_str.endswith("}"):
            # Dict
            inner = value_str[1:-1]
            if not inner:
                return {}
            result = {}
            for item in inner.split(","):
                if "=" in item:
                    k, v = item.split("=", 1)
                    result[k] = self._deserialize_value(v)
            return result
        else:
            # Try JSON deserialization
            try:
                return json.loads(value_str)
            except (TypeError, ValueError):
                return value_str


# Global key generator instance
_default_generator = CacheKeyGenerator()


def generate_cache_key(
    service_name: str,
    method_name: str,
    args: tuple = (),
    kwargs: Optional[Dict[str, Any]] = None,
    prefix: str = "congress_cache"
) -> str:
    """
    Generate a cache key using the default generator.
    
    Args:
        service_name: Name of the service
        method_name: Name of the method
        args: Positional arguments
        kwargs: Keyword arguments
        prefix: Key prefix
        
    Returns:
        Generated cache key
    """
    return _default_generator.generate_key(service_name, method_name, args, kwargs, prefix)


def generate_pattern_key(
    service_name: str,
    method_name: str,
    pattern: str = "*"
) -> str:
    """
    Generate a pattern key using the default generator.
    
    Args:
        service_name: Name of the service
        method_name: Name of the method
        pattern: Pattern to match
        
    Returns:
        Pattern key
    """
    return _default_generator.generate_pattern_key(service_name, method_name, pattern)


# Common key patterns for different services
SERVICE_PATTERNS = {
    "bill": {
        "get": "bill:get:{congress}:{bill_type}:{bill_number}",
        "search": "bill:search:{congress}:{bill_type}:{limit}:{offset}",
        "actions": "bill:actions:{congress}:{bill_type}:{bill_number}",
        "cosponsors": "bill:cosponsors:{congress}:{bill_type}:{bill_number}",
    },
    "member": {
        "get": "member:get:{bioguide_id}",
        "search": "member:search:{congress}:{state}:{party}",
        "bills": "member:bills:{bioguide_id}:{congress}",
    },
    "committee": {
        "get": "committee:get:{chamber}:{committee_code}",
        "search": "committee:search:{congress}:{chamber}",
        "bills": "committee:bills:{chamber}:{committee_code}:{congress}",
    },
}
