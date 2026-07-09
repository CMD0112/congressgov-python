"""Cache invalidation based on data relationships, time-based rules, and pattern matching."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
import logging
import time
import fnmatch
from dataclasses import dataclass

from .config import CacheInvalidationConfig

logger = logging.getLogger(__name__)


@dataclass
class InvalidationRule:
    """A rule specifying when and how matching cache entries get invalidated."""
    
    name: str
    patterns: List[str]
    trigger_events: List[str]
    conditions: Optional[Callable] = None
    priority: int = 0  # Higher priority rules are checked first


class CacheInvalidator:
    """Invalidates cache entries via rules keyed on data relationships, time,
    glob patterns, or trigger events - e.g. invalidate bill actions when the
    parent bill changes, expire entries after a fixed window, or wipe
    everything matching a pattern.
    """
    
    def __init__(
        self,
        config: Optional[CacheInvalidationConfig] = None,
        cache_backend: Optional[Any] = None
    ):
        """
        Initialize cache invalidator.
        
        Args:
            config: Invalidation configuration
            cache_backend: Cache backend to invalidate
        """
        self.config = config or CacheInvalidationConfig()
        self.cache_backend = cache_backend
        
        # Invalidation rules
        self.rules: List[InvalidationRule] = []
        self._setup_default_rules()
        
        # Event tracking
        self._event_history: List[Dict[str, Any]] = []
        self._max_event_history = 1000
        
        # Pattern cache for performance
        self._pattern_cache: Dict[str, List[str]] = {}
        
        logger.info("Cache invalidator initialized")
    
    def _setup_default_rules(self):
        """Set up default invalidation rules."""
        # Bill-related invalidation rules
        self.add_rule(InvalidationRule(
            name="bill_update",
            patterns=["bill:*", "bill_actions:*", "bill_cosponsors:*", "bill_summaries:*"],
            trigger_events=["bill_updated", "bill_modified"],
            priority=10
        ))
        
        # Member-related invalidation rules
        self.add_rule(InvalidationRule(
            name="member_update",
            patterns=["member:*", "member_bills:*", "member_committees:*"],
            trigger_events=["member_updated", "member_modified"],
            priority=10
        ))
        
        # Committee-related invalidation rules
        self.add_rule(InvalidationRule(
            name="committee_update",
            patterns=["committee:*", "committee_bills:*", "committee_members:*"],
            trigger_events=["committee_updated", "committee_modified"],
            priority=10
        ))
        
        # Time-based invalidation
        self.add_rule(InvalidationRule(
            name="time_based",
            patterns=["*"],
            trigger_events=["time_expired"],
            conditions=lambda: self.config.enable_time_based,
            priority=5
        ))
    
    def add_rule(self, rule: InvalidationRule):
        """
        Add an invalidation rule.
        
        Args:
            rule: The invalidation rule to add
        """
        self.rules.append(rule)
        # Sort by priority (higher priority first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.debug(f"Added invalidation rule: {rule.name}")
    
    def remove_rule(self, name: str) -> bool:
        """
        Remove an invalidation rule by name.
        
        Args:
            name: Name of the rule to remove
            
        Returns:
            True if rule was removed, False if not found
        """
        for i, rule in enumerate(self.rules):
            if rule.name == name:
                del self.rules[i]
                logger.debug(f"Removed invalidation rule: {name}")
                return True
        return False
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match (supports wildcards)
            
        Returns:
            Number of entries invalidated
        """
        if not self.cache_backend:
            logger.warning("No cache backend configured for invalidation")
            return 0
        
        try:
            # Get all keys matching the pattern
            matching_keys = self._get_matching_keys(pattern)
            
            # Delete matching keys
            invalidated = 0
            for key in matching_keys:
                if self.cache_backend.delete(key):
                    invalidated += 1
            
            logger.info(f"Invalidated {invalidated} entries matching pattern: {pattern}")
            return invalidated
            
        except Exception as e:
            logger.error(f"Failed to invalidate pattern '{pattern}': {e}")
            return 0
    
    def invalidate_by_event(self, event: str, context: Optional[Dict[str, Any]] = None) -> int:
        """
        Invalidate cache entries based on an event.
        
        Args:
            event: The event that triggered invalidation
            context: Additional context about the event
            
        Returns:
            Number of entries invalidated
        """
        # Record the event
        self._record_event(event, context)
        
        # Find applicable rules
        applicable_rules = [
            rule for rule in self.rules
            if event in rule.trigger_events
            and (rule.conditions is None or rule.conditions())
        ]
        
        if not applicable_rules:
            logger.debug(f"No invalidation rules found for event: {event}")
            return 0
        
        # Invalidate based on rules
        total_invalidated = 0
        for rule in applicable_rules:
            for pattern in rule.patterns:
                invalidated = self.invalidate_by_pattern(pattern)
                total_invalidated += invalidated
                logger.debug(f"Rule '{rule.name}' invalidated {invalidated} entries for pattern: {pattern}")
        
        logger.info(f"Event '{event}' invalidated {total_invalidated} total entries")
        return total_invalidated
    
    def invalidate_related(self, entity_type: str, entity_id: str) -> int:
        """
        Invalidate cache entries related to a specific entity.
        
        Args:
            entity_type: Type of entity (e.g., 'bill', 'member')
            entity_id: ID of the entity
            
        Returns:
            Number of entries invalidated
        """
        # Get invalidation patterns for this entity type
        patterns = self.config.get_invalidation_patterns(entity_type)
        
        # Add entity-specific patterns
        entity_patterns = [
            f"{entity_type}:{entity_id}:*",
            f"{entity_type}:*:{entity_id}:*",
            f"*:{entity_type}:{entity_id}:*"
        ]
        patterns.extend(entity_patterns)
        
        # Invalidate all patterns
        total_invalidated = 0
        for pattern in patterns:
            invalidated = self.invalidate_by_pattern(pattern)
            total_invalidated += invalidated
        
        logger.info(f"Invalidated {total_invalidated} entries related to {entity_type}:{entity_id}")
        return total_invalidated
    
    def invalidate_old_entries(self, max_age: int) -> int:
        """
        Invalidate entries older than max_age.
        
        Args:
            max_age: Maximum age in seconds
            
        Returns:
            Number of entries invalidated
        """
        if not self.config.enable_time_based:
            return 0
        
        try:
            # This is a simplified implementation
            # In practice, you'd need to track creation times
            # or use a TTL-based approach
            
            # For now, invalidate all entries
            # In a real implementation, you'd check timestamps
            if hasattr(self.cache_backend, 'clear'):
                self.cache_backend.clear()
                logger.info("Cleared all cache entries (time-based invalidation)")
                return 1  # Return 1 to indicate some action was taken
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to invalidate old entries: {e}")
            return 0
    
    def _get_matching_keys(self, pattern: str) -> List[str]:
        """
        Get all cache keys matching a pattern.
        
        Args:
            pattern: Pattern to match
            
        Returns:
            List of matching keys
        """
        if not self.cache_backend:
            return []
        
        try:
            # Check pattern cache first
            if pattern in self._pattern_cache:
                return self._pattern_cache[pattern]
            
            # Get all keys (this is backend-specific)
            if hasattr(self.cache_backend, 'keys'):
                all_keys = self.cache_backend.keys()
            elif hasattr(self.cache_backend, 'scan_keys'):
                all_keys = list(self.cache_backend.scan_keys())
            else:
                # Fallback: can't get all keys
                logger.warning("Cache backend doesn't support key enumeration")
                return []
            
            # Filter keys matching pattern
            matching_keys = [
                key for key in all_keys
                if fnmatch.fnmatch(key, pattern)
            ]
            
            # Cache the result
            self._pattern_cache[pattern] = matching_keys
            
            return matching_keys
            
        except Exception as e:
            logger.error(f"Failed to get matching keys for pattern '{pattern}': {e}")
            return []
    
    def _record_event(self, event: str, context: Optional[Dict[str, Any]] = None):
        """
        Record an invalidation event.
        
        Args:
            event: Event name
            context: Event context
        """
        event_record = {
            'event': event,
            'timestamp': time.time(),
            'context': context or {}
        }
        
        self._event_history.append(event_record)
        
        # Limit history size
        if len(self._event_history) > self._max_event_history:
            self._event_history = self._event_history[-self._max_event_history:]
    
    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent invalidation events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        return self._event_history[-limit:]
    
    def get_invalidation_stats(self) -> Dict[str, Any]:
        """
        Get invalidation statistics.
        
        Returns:
            Dictionary with invalidation statistics
        """
        return {
            'total_rules': len(self.rules),
            'total_events': len(self._event_history),
            'recent_events': len(self._event_history[-10:]),
            'pattern_cache_size': len(self._pattern_cache),
            'rules': [
                {
                    'name': rule.name,
                    'patterns': rule.patterns,
                    'trigger_events': rule.trigger_events,
                    'priority': rule.priority
                }
                for rule in self.rules
            ]
        }
    
    def clear_pattern_cache(self):
        """Clear the pattern matching cache."""
        self._pattern_cache.clear()
        logger.debug("Cleared pattern cache")
    
    def cleanup_old_events(self, max_age: int = 3600):
        """
        Clean up old events from history.
        
        Args:
            max_age: Maximum age in seconds
        """
        current_time = time.time()
        cutoff_time = current_time - max_age
        
        # Remove old events
        self._event_history = [
            event for event in self._event_history
            if event['timestamp'] > cutoff_time
        ]
        
        logger.debug(f"Cleaned up old events, {len(self._event_history)} remaining")


# Convenience functions for common invalidation patterns
def invalidate_bill_data(invalidator: CacheInvalidator, bill_id: str) -> int:
    """Invalidate all data related to a specific bill."""
    return invalidator.invalidate_related("bill", bill_id)


def invalidate_member_data(invalidator: CacheInvalidator, member_id: str) -> int:
    """Invalidate all data related to a specific member."""
    return invalidator.invalidate_related("member", member_id)


def invalidate_committee_data(invalidator: CacheInvalidator, committee_id: str) -> int:
    """Invalidate all data related to a specific committee."""
    return invalidator.invalidate_related("committee", committee_id)


def invalidate_search_results(invalidator: CacheInvalidator) -> int:
    """Invalidate all search result caches."""
    return invalidator.invalidate_by_pattern("*:search:*")







