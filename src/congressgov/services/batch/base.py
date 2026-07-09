"""
Base batch processing infrastructure and configuration.

This module provides the foundational classes and utilities for batch processing,
including configuration, result tracking, and common batch processing utilities.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """Status of a batch operation."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RetryStrategy(Enum):
    """Retry strategy for failed operations."""
    
    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


@dataclass
class BatchConfig:
    """
    Configuration for batch processing operations.
    
    This class provides comprehensive configuration options for all batch
    processing operations, including concurrency, retry logic, and monitoring.
    """
    
    # Concurrency settings
    max_concurrent: int = 10
    batch_size: int = 50
    chunk_size: int = 20
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retry_multiplier: float = 2.0
    max_retry_delay: float = 60.0
    
    # Memory settings
    max_memory_mb: Optional[int] = None
    memory_check_interval: int = 100  # Check every N items
    gc_interval: int = 1000  # Force GC every N items
    
    # Progress tracking
    progress_callback: Optional[Callable[[float], None]] = None
    progress_interval: float = 0.1  # Update every 10% by default
    
    # Error handling
    continue_on_error: bool = True
    error_callback: Optional[Callable[[Exception, Any], None]] = None
    success_callback: Optional[Callable[[Any], None]] = None
    
    # Checkpoint settings
    checkpoint_interval: int = 1000  # Save checkpoint every N items
    checkpoint_file: Optional[str] = None
    
    # Timeout settings
    operation_timeout: Optional[float] = None
    batch_timeout: Optional[float] = None
    
    # Circuit breaker settings
    circuit_breaker_threshold: int = 10  # Failures before opening circuit
    circuit_breaker_timeout: float = 60.0  # Time before trying half-open
    
    def get_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay based on strategy and attempt number."""
        if self.retry_strategy == RetryStrategy.NONE:
            return 0.0
        elif self.retry_strategy == RetryStrategy.FIXED:
            return self.retry_delay
        elif self.retry_strategy == RetryStrategy.LINEAR:
            return self.retry_delay * attempt
        elif self.retry_strategy == RetryStrategy.EXPONENTIAL:
            delay = self.retry_delay * (self.retry_multiplier ** (attempt - 1))
            return min(delay, self.max_retry_delay)
        else:
            return self.retry_delay
    
    def should_retry(self, attempt: int) -> bool:
        """Check if operation should be retried."""
        return attempt <= self.max_retries and self.retry_strategy != RetryStrategy.NONE


@dataclass
class BatchResult:
    """
    Result of a batch processing operation.
    
    This class tracks the results of batch operations including success/failure
    counts, timing information, and error details.
    """
    
    # Operation details
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    retried_items: int = 0
    
    # Timing information
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[timedelta] = None
    
    # Results
    results: List[Any] = field(default_factory=list)
    errors: List[tuple[Any, Exception]] = field(default_factory=list)
    failed_items_list: List[Any] = field(default_factory=list)
    
    # Performance metrics
    items_per_second: float = 0.0
    memory_peak_mb: float = 0.0
    api_calls_made: int = 0
    
    # Status
    status: BatchStatus = BatchStatus.PENDING
    cancelled: bool = False
    
    # Callbacks (set by processor)
    success_callback: Optional[Callable[[Any], None]] = None
    error_callback: Optional[Callable[[Exception, Any], None]] = None
    
    def __post_init__(self):
        """Initialize timing if not provided."""
        if self.start_time is None:
            self.start_time = datetime.now()
    
    def add_success(self, item: Any, result: Any) -> None:
        """Add a successful item to the result."""
        self.successful_items += 1
        self.processed_items += 1
        self.results.append(result)
        
        if self.success_callback:
            try:
                self.success_callback(item)
            except Exception as e:
                logger.warning(f"Success callback failed: {e}")
    
    def add_failure(self, item: Any, error: Exception) -> None:
        """Add a failed item to the result."""
        self.failed_items += 1
        self.processed_items += 1
        self.errors.append((item, error))
        self.failed_items_list.append(item)
        
        if self.error_callback:
            try:
                self.error_callback(error, item)
            except Exception as e:
                logger.warning(f"Error callback failed: {e}")
    
    def add_retry(self, item: Any) -> None:
        """Add a retry to the result."""
        self.retried_items += 1
    
    def complete(self) -> None:
        """Mark the batch as completed."""
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        self.status = BatchStatus.COMPLETED
        
        # Calculate performance metrics
        if self.duration and self.duration.total_seconds() > 0:
            self.items_per_second = self.processed_items / self.duration.total_seconds()
    
    def fail(self) -> None:
        """Mark the batch as failed."""
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        self.status = BatchStatus.FAILED
    
    def cancel(self) -> None:
        """Mark the batch as cancelled."""
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        self.status = BatchStatus.CANCELLED
        self.cancelled = True
    
    def get_success_rate(self) -> float:
        """Get the success rate as a percentage."""
        if self.processed_items == 0:
            return 0.0
        return (self.successful_items / self.processed_items) * 100.0
    
    def get_progress(self) -> float:
        """Get the progress as a percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100.0
    
    def get_remaining_time(self) -> Optional[timedelta]:
        """Estimate remaining time based on current processing rate."""
        if not self.items_per_second or self.items_per_second == 0:
            return None
        
        remaining_items = self.total_items - self.processed_items
        remaining_seconds = remaining_items / self.items_per_second
        return timedelta(seconds=remaining_seconds)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            'total_items': self.total_items,
            'processed_items': self.processed_items,
            'successful_items': self.successful_items,
            'failed_items': self.failed_items,
            'retried_items': self.retried_items,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration.total_seconds() if self.duration else None,
            'items_per_second': self.items_per_second,
            'memory_peak_mb': self.memory_peak_mb,
            'api_calls_made': self.api_calls_made,
            'status': self.status.value,
            'cancelled': self.cancelled,
            'success_rate': self.get_success_rate(),
            'progress': self.get_progress(),
            'remaining_time_seconds': self.get_remaining_time().total_seconds() if self.get_remaining_time() else None,
            'error_count': len(self.errors)
        }


class BaseBatchProcessor(ABC):
    """
    Abstract base class for all batch processors.
    
    This class provides common functionality for batch processing operations,
    including configuration management, progress tracking, and error handling.
    """
    
    def __init__(self, config: Optional[BatchConfig] = None):
        """
        Initialize the batch processor.
        
        Args:
            config: Batch configuration (uses default if None)
        """
        self.config = config or BatchConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cancelled = False
        self._start_time: Optional[datetime] = None
    
    @abstractmethod
    async def process_batch(self, items: List[Any], operation: Callable[[Any], Any]) -> BatchResult:
        """
        Process a batch of items.
        
        Args:
            items: List of items to process
            operation: Function to apply to each item
            
        Returns:
            BatchResult with processing details
        """
        pass
    
    def cancel(self) -> None:
        """Cancel the current batch operation."""
        self._cancelled = True
        self.logger.info("Batch operation cancelled")
    
    def is_cancelled(self) -> bool:
        """Check if the batch operation has been cancelled."""
        return self._cancelled
    
    def _update_progress(self, result: BatchResult) -> None:
        """Update progress if callback is configured."""
        if self.config.progress_callback and result.total_items > 0:
            progress = result.get_progress()
            self.config.progress_callback(progress)
    
    def _should_checkpoint(self, result: BatchResult) -> bool:
        """Check if a checkpoint should be saved."""
        return (
            self.config.checkpoint_interval > 0 and
            result.processed_items > 0 and
            result.processed_items % self.config.checkpoint_interval == 0
        )
    
    def _log_performance(self, result: BatchResult) -> None:
        """Log performance metrics."""
        if result.duration:
            self.logger.info(
                f"Batch completed: {result.successful_items}/{result.total_items} successful "
                f"({result.get_success_rate():.1f}%) in {result.duration.total_seconds():.2f}s "
                f"({result.items_per_second:.1f} items/sec)"
            )
    
    def _create_result(self, total_items: int) -> BatchResult:
        """Create a new batch result."""
        result = BatchResult(total_items=total_items)
        result.start_time = datetime.now()
        result.success_callback = self.config.success_callback
        result.error_callback = self.config.error_callback
        self._start_time = result.start_time
        return result


class BatchProcessorMixin:
    """Mixin class providing common batch processing utilities."""
    
    @staticmethod
    async def _run_with_timeout(
        coro: Any,
        timeout: Optional[float] = None,
        operation_name: str = "operation"
    ) -> Any:
        """Run a coroutine with optional timeout."""
        if timeout:
            try:
                return await asyncio.wait_for(coro, timeout=timeout)
            except asyncio.TimeoutError:
                raise TimeoutError(f"{operation_name} timed out after {timeout}s")
        else:
            return await coro
    
    @staticmethod
    async def _retry_operation(
        operation: Callable[[], Any],
        max_retries: int,
        retry_delay: float,
        retry_strategy: RetryStrategy,
        retry_multiplier: float,
        max_retry_delay: float,
        operation_name: str = "operation"
    ) -> Any:
        """Retry an operation with configurable strategy."""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await operation()
            except Exception as e:
                last_error = e
                
                if attempt < max_retries:
                    delay = BatchConfig(
                        retry_strategy=retry_strategy,
                        retry_delay=retry_delay,
                        retry_multiplier=retry_multiplier,
                        max_retry_delay=max_retry_delay
                    ).get_retry_delay(attempt + 1)
                    
                    logger.warning(
                        f"{operation_name} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{operation_name} failed after {max_retries + 1} attempts: {e}")
        
        raise last_error
    
    @staticmethod
    def _create_operation_wrapper(
        operation: Callable[[Any], Any],
        timeout: Optional[float] = None,
        operation_name: str = "operation"
    ) -> Callable[[Any], Any]:
        """Create a wrapper for an operation with timeout and error handling."""
        async def wrapper(item: Any) -> Any:
            try:
                if asyncio.iscoroutinefunction(operation):
                    result = await BatchProcessorMixin._run_with_timeout(
                        operation(item), timeout, operation_name
                    )
                else:
                    # Run sync function in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, operation, item)
                
                return result
            except Exception as e:
                logger.error(f"Operation failed for item {item}: {e}")
                raise
        
        return wrapper
