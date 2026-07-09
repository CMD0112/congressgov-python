"""Tracks failed batch items, schedules retries, and reports recovery statistics."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Strategy for recovering failed items."""
    
    IMMEDIATE = "immediate"  # Retry immediately
    EXPONENTIAL = "exponential"  # Exponential backoff
    LINEAR = "linear"  # Linear backoff
    FIXED = "fixed"  # Fixed delay
    SCHEDULED = "scheduled"  # Scheduled retry


@dataclass
class FailedItem:
    """Represents a failed item with retry information."""
    
    item: Any
    error: Exception
    attempt_count: int = 0
    first_failure_time: datetime = field(default_factory=datetime.now)
    last_failure_time: datetime = field(default_factory=datetime.now)
    next_retry_time: Optional[datetime] = None
    priority: int = 0  # Higher number = higher priority
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if not self.first_failure_time:
            self.first_failure_time = datetime.now()
        if not self.last_failure_time:
            self.last_failure_time = datetime.now()


@dataclass
class RecoveryStats:
    """Statistics for error recovery operations."""
    
    total_failed_items: int = 0
    recovered_items: int = 0
    permanently_failed_items: int = 0
    total_retry_attempts: int = 0
    average_recovery_time: float = 0.0
    recovery_success_rate: float = 0.0
    
    def update_recovery_time(self, recovery_time: float) -> None:
        """Update average recovery time."""
        if self.recovered_items == 0:
            self.average_recovery_time = recovery_time
        else:
            # Running average
            self.average_recovery_time = (
                (self.average_recovery_time * (self.recovered_items - 1) + recovery_time) /
                self.recovered_items
            )
    
    def get_stats_dict(self) -> Dict[str, Any]:
        """Get statistics as dictionary."""
        return {
            'total_failed_items': self.total_failed_items,
            'recovered_items': self.recovered_items,
            'permanently_failed_items': self.permanently_failed_items,
            'total_retry_attempts': self.total_retry_attempts,
            'average_recovery_time': self.average_recovery_time,
            'recovery_success_rate': self.recovery_success_rate
        }


class ErrorRecoveryManager:
    """
    Error recovery manager for batch operations.
    
    This class manages failed items, schedules retries, and tracks recovery
    statistics for batch processing operations.
    
    Example:
        manager = ErrorRecoveryManager(
            max_retries=3,
            retry_delay=2.0,
            recovery_strategy=RecoveryStrategy.EXPONENTIAL
        )
        
        # Add failed item
        manager.add_failed_item(item, error)
        
        # Process recovery queue
        recovered = await manager.process_recovery_queue(operation)
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.EXPONENTIAL,
        max_retry_delay: float = 300.0,  # 5 minutes
        priority_enabled: bool = True
    ):
        """
        Initialize the error recovery manager.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries
            recovery_strategy: Strategy for calculating retry delays
            max_retry_delay: Maximum delay between retries
            priority_enabled: Whether to use priority-based scheduling
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.recovery_strategy = recovery_strategy
        self.max_retry_delay = max_retry_delay
        self.priority_enabled = priority_enabled
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self._failed_items: List[FailedItem] = []
        self._recovery_queue: List[FailedItem] = []
        self._stats = RecoveryStats()
        self._processing = False
    
    def add_failed_item(
        self,
        item: Any,
        error: Exception,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a failed item to the recovery queue.
        
        Args:
            item: The failed item
            error: The error that occurred
            priority: Priority for recovery (higher = more important)
            metadata: Additional metadata for the item
        """
        failed_item = FailedItem(
            item=item,
            error=error,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Calculate next retry time
        failed_item.next_retry_time = self._calculate_next_retry_time(failed_item)
        
        self._failed_items.append(failed_item)
        self._recovery_queue.append(failed_item)
        self._stats.total_failed_items += 1
        
        # Sort by priority and retry time
        if self.priority_enabled:
            self._recovery_queue.sort(key=lambda x: (-x.priority, x.next_retry_time or datetime.max))
        else:
            self._recovery_queue.sort(key=lambda x: x.next_retry_time or datetime.max)
        
        self.logger.debug(f"Added failed item to recovery queue: {item}")
    
    def _calculate_next_retry_time(self, failed_item: FailedItem) -> datetime:
        """Calculate the next retry time for a failed item."""
        if failed_item.attempt_count >= self.max_retries:
            return datetime.max  # Never retry
        
        base_delay = self.retry_delay
        
        if self.recovery_strategy == RecoveryStrategy.IMMEDIATE:
            delay = 0
        elif self.recovery_strategy == RecoveryStrategy.FIXED:
            delay = base_delay
        elif self.recovery_strategy == RecoveryStrategy.LINEAR:
            delay = base_delay * (failed_item.attempt_count + 1)
        elif self.recovery_strategy == RecoveryStrategy.EXPONENTIAL:
            delay = base_delay * (2 ** failed_item.attempt_count)
        elif self.recovery_strategy == RecoveryStrategy.SCHEDULED:
            # Use metadata to determine delay
            delay = failed_item.metadata.get('retry_delay', base_delay)
        else:
            delay = base_delay
        
        # Cap the delay
        delay = min(delay, self.max_retry_delay)
        
        return datetime.now() + timedelta(seconds=delay)
    
    async def process_recovery_queue(
        self,
        operation: Callable[[Any], Any],
        max_concurrent: int = 5
    ) -> List[Any]:
        """
        Process the recovery queue with the given operation.
        
        Args:
            operation: Operation to apply to items
            max_concurrent: Maximum concurrent recovery operations
            
        Returns:
            List of successfully recovered items
        """
        if self._processing:
            self.logger.warning("Recovery queue is already being processed")
            return []
        
        self._processing = True
        recovered_items = []
        
        try:
            # Filter items ready for retry
            ready_items = [
                item for item in self._recovery_queue
                if item.next_retry_time and item.next_retry_time <= datetime.now()
            ]
            
            if not ready_items:
                self.logger.debug("No items ready for recovery")
                return []
            
            self.logger.info(f"Processing {len(ready_items)} items for recovery")
            
            # Process items with concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)
            tasks = []
            
            for failed_item in ready_items:
                task = asyncio.create_task(
                    self._recover_item(failed_item, operation, semaphore)
                )
                tasks.append(task)
            
            # Wait for all recovery tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Recovery task failed: {result}")
                else:
                    recovered_items.append(result)
            
            # Update statistics
            self._stats.recovered_items += len(recovered_items)
            self._stats.recovery_success_rate = (
                self._stats.recovered_items / self._stats.total_failed_items * 100.0
                if self._stats.total_failed_items > 0 else 0.0
            )
            
            self.logger.info(f"Recovery completed: {len(recovered_items)} items recovered")
            
        except Exception as e:
            self.logger.error(f"Recovery queue processing failed: {e}")
            raise
        finally:
            self._processing = False
        
        return recovered_items
    
    async def _recover_item(
        self,
        failed_item: FailedItem,
        operation: Callable[[Any], Any],
        semaphore: asyncio.Semaphore
    ) -> Any:
        """
        Attempt to recover a single failed item.
        
        Args:
            failed_item: The failed item to recover
            operation: Operation to apply to the item
            semaphore: Semaphore for concurrency control
            
        Returns:
            Recovered item or raises exception
        """
        async with semaphore:
            start_time = time.time()
            
            try:
                # Update attempt count
                failed_item.attempt_count += 1
                failed_item.last_failure_time = datetime.now()
                self._stats.total_retry_attempts += 1
                
                # Attempt recovery
                if asyncio.iscoroutinefunction(operation):
                    result = await operation(failed_item.item)
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, operation, failed_item.item)
                
                # Recovery successful
                recovery_time = time.time() - start_time
                self._stats.update_recovery_time(recovery_time)
                
                # Remove from queues
                self._recovery_queue.remove(failed_item)
                self._failed_items.remove(failed_item)
                
                self.logger.debug(f"Successfully recovered item: {failed_item.item}")
                return result
                
            except Exception as e:
                # Recovery failed
                self.logger.warning(f"Recovery failed for item {failed_item.item}: {e}")
                
                # Check if we should retry again
                if failed_item.attempt_count < self.max_retries:
                    # Schedule next retry
                    failed_item.next_retry_time = self._calculate_next_retry_time(failed_item)
                    self.logger.debug(f"Scheduled retry for item {failed_item.item} at {failed_item.next_retry_time}")
                else:
                    # Permanently failed
                    self._stats.permanently_failed_items += 1
                    self._recovery_queue.remove(failed_item)
                    self.logger.error(f"Item permanently failed after {self.max_retries} attempts: {failed_item.item}")
                
                raise e
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics."""
        return self._stats.get_stats_dict()
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        ready_count = len([
            item for item in self._recovery_queue
            if item.next_retry_time and item.next_retry_time <= datetime.now()
        ])
        
        return {
            'total_failed_items': len(self._failed_items),
            'recovery_queue_size': len(self._recovery_queue),
            'ready_for_retry': ready_count,
            'processing': self._processing,
            'max_retries': self.max_retries,
            'recovery_strategy': self.recovery_strategy.value
        }
    
    def clear_failed_items(self) -> None:
        """Clear all failed items and reset statistics."""
        self._failed_items.clear()
        self._recovery_queue.clear()
        self._stats = RecoveryStats()
        self.logger.info("Cleared all failed items and reset statistics")
    
    def remove_item(self, item: Any) -> bool:
        """
        Remove a specific item from the recovery queue.
        
        Args:
            item: Item to remove
            
        Returns:
            True if item was found and removed
        """
        removed = False
        
        # Remove from failed items
        for failed_item in self._failed_items[:]:
            if failed_item.item == item:
                self._failed_items.remove(failed_item)
                removed = True
        
        # Remove from recovery queue
        for failed_item in self._recovery_queue[:]:
            if failed_item.item == item:
                self._recovery_queue.remove(failed_item)
                removed = True
        
        if removed:
            self.logger.debug(f"Removed item from recovery queue: {item}")
        
        return removed
    
    def get_failed_items(self) -> List[Any]:
        """Get list of all failed items."""
        return [item.item for item in self._failed_items]
    
    def get_ready_items(self) -> List[Any]:
        """Get list of items ready for retry."""
        return [
            item.item for item in self._recovery_queue
            if item.next_retry_time and item.next_retry_time <= datetime.now()
        ]
    
    def set_item_priority(self, item: Any, priority: int) -> bool:
        """
        Set priority for a specific item.
        
        Args:
            item: Item to update
            priority: New priority value
            
        Returns:
            True if item was found and updated
        """
        updated = False
        
        for failed_item in self._failed_items:
            if failed_item.item == item:
                failed_item.priority = priority
                updated = True
        
        # Re-sort recovery queue by priority
        if updated and self.priority_enabled:
            self._recovery_queue.sort(key=lambda x: (-x.priority, x.next_retry_time or datetime.max))
        
        return updated







