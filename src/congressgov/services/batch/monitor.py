"""
Batch monitoring and progress tracking.

This module provides the BatchMonitor class for comprehensive progress tracking,
performance monitoring, and real-time metrics collection.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Callable
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    tqdm = None

logger = logging.getLogger(__name__)


@dataclass
class BatchMetrics:
    """Metrics for batch processing operations."""
    
    # Processing metrics
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    retried_items: int = 0
    
    # Timing metrics
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[timedelta] = None
    
    # Performance metrics
    items_per_second: float = 0.0
    estimated_remaining_time: Optional[timedelta] = None
    
    # Memory metrics
    memory_peak_mb: float = 0.0
    memory_current_mb: float = 0.0
    
    # API metrics
    api_calls_made: int = 0
    api_calls_failed: int = 0
    
    # Error metrics
    error_count: int = 0
    error_types: Dict[str, int] = field(default_factory=dict)
    
    def update_processing(self, processed: int, successful: int, failed: int) -> None:
        """Update processing metrics."""
        self.processed_items = processed
        self.successful_items = successful
        self.failed_items = failed
        
        # Calculate items per second
        if self.start_time and self.duration:
            self.items_per_second = processed / self.duration.total_seconds()
    
    def update_timing(self, start: Optional[datetime] = None, end: Optional[datetime] = None) -> None:
        """Update timing metrics."""
        if start:
            self.start_time = start
        if end:
            self.end_time = end
        
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
    
    def update_memory(self, peak_mb: float, current_mb: float) -> None:
        """Update memory metrics."""
        self.memory_peak_mb = peak_mb
        self.memory_current_mb = current_mb
    
    def update_api_calls(self, made: int, failed: int) -> None:
        """Update API call metrics."""
        self.api_calls_made = made
        self.api_calls_failed = failed
    
    def add_error(self, error_type: str) -> None:
        """Add an error to the metrics."""
        self.error_count += 1
        self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.processed_items == 0:
            return 0.0
        return (self.successful_items / self.processed_items) * 100.0
    
    def get_progress(self) -> float:
        """Get progress as percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100.0
    
    def get_estimated_remaining_time(self) -> Optional[timedelta]:
        """Get estimated remaining time."""
        if not self.items_per_second or self.items_per_second == 0:
            return None
        
        remaining_items = self.total_items - self.processed_items
        remaining_seconds = remaining_items / self.items_per_second
        return timedelta(seconds=remaining_seconds)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
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
            'estimated_remaining_time_seconds': self.get_estimated_remaining_time().total_seconds() if self.get_estimated_remaining_time() else None,
            'memory_peak_mb': self.memory_peak_mb,
            'memory_current_mb': self.memory_current_mb,
            'api_calls_made': self.api_calls_made,
            'api_calls_failed': self.api_calls_failed,
            'error_count': self.error_count,
            'error_types': self.error_types.copy(),
            'success_rate': self.get_success_rate(),
            'progress': self.get_progress()
        }


class BatchMonitor:
    """
    Batch monitor for comprehensive progress tracking.
    
    This class provides real-time monitoring of batch operations including
    progress tracking, performance metrics, and integration with progress bars.
    
    Example:
        monitor = BatchMonitor(
            total_items=1000,
            progress_bar=tqdm(desc="Processing bills")
        )
        
        # Update progress
        monitor.update(100)
        
        # Get metrics
        metrics = monitor.get_metrics()
    """
    
    def __init__(
        self,
        total_items: int = 0,
        progress_bar: Optional[Any] = None,
        metrics_callback: Optional[Callable[[BatchMetrics], None]] = None,
        checkpoint_callback: Optional[Callable[[BatchMetrics], None]] = None,
        update_interval: float = 1.0  # Update every second
    ):
        """
        Initialize the batch monitor.
        
        Args:
            total_items: Total number of items to process
            progress_bar: Progress bar instance (e.g., tqdm)
            metrics_callback: Callback for metrics updates
            checkpoint_callback: Callback for checkpoint saves
            update_interval: Interval for automatic updates
        """
        self.total_items = total_items
        self.progress_bar = progress_bar
        self.metrics_callback = metrics_callback
        self.checkpoint_callback = checkpoint_callback
        self.update_interval = update_interval
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self._metrics = BatchMetrics(total_items=total_items)
        self._last_update_time = time.time()
        self._start_time = datetime.now()
        self._cancelled = False
    
    def update(self, items_processed: int, **kwargs) -> None:
        """
        Update the monitor with current progress.
        
        Args:
            items_processed: Number of items processed so far
            **kwargs: Additional metrics to update
        """
        if self._cancelled:
            return
        
        # Update metrics
        self._metrics.processed_items = items_processed
        
        # Update additional metrics
        for key, value in kwargs.items():
            if hasattr(self._metrics, key):
                setattr(self._metrics, key, value)
        
        # Update timing
        self._metrics.update_timing(start=self._start_time, end=datetime.now())
        
        # Update progress bar
        if self.progress_bar:
            self.progress_bar.update(items_processed - self.progress_bar.n)
        
        # Check if we should trigger callbacks
        current_time = time.time()
        if current_time - self._last_update_time >= self.update_interval:
            self._trigger_callbacks()
            self._last_update_time = current_time
    
    def update_success(self, count: int = 1) -> None:
        """Update successful items count."""
        self._metrics.successful_items += count
        self._update_metrics()
    
    def update_failure(self, count: int = 1, error_type: Optional[str] = None) -> None:
        """Update failed items count."""
        self._metrics.failed_items += count
        if error_type:
            self._metrics.add_error(error_type)
        self._update_metrics()
    
    def update_retry(self, count: int = 1) -> None:
        """Update retried items count."""
        self._metrics.retried_items += count
        self._update_metrics()
    
    def update_memory(self, peak_mb: float, current_mb: float) -> None:
        """Update memory metrics."""
        self._metrics.update_memory(peak_mb, current_mb)
        self._update_metrics()
    
    def update_api_calls(self, made: int, failed: int) -> None:
        """Update API call metrics."""
        self._metrics.update_api_calls(made, failed)
        self._update_metrics()
    
    def _update_metrics(self) -> None:
        """Update internal metrics and trigger callbacks if needed."""
        current_time = time.time()
        if current_time - self._last_update_time >= self.update_interval:
            self._trigger_callbacks()
            self._last_update_time = current_time
    
    def _trigger_callbacks(self) -> None:
        """Trigger registered callbacks."""
        # Update progress bar
        if self.progress_bar:
            self.progress_bar.set_postfix({
                'success_rate': f"{self._metrics.get_success_rate():.1f}%",
                'items/sec': f"{self._metrics.items_per_second:.1f}",
                'memory_mb': f"{self._metrics.memory_current_mb:.1f}"
            })
        
        # Trigger metrics callback
        if self.metrics_callback:
            try:
                self.metrics_callback(self._metrics)
            except Exception as e:
                self.logger.error(f"Metrics callback failed: {e}")
        
        # Trigger checkpoint callback
        if self.checkpoint_callback:
            try:
                self.checkpoint_callback(self._metrics)
            except Exception as e:
                self.logger.error(f"Checkpoint callback failed: {e}")
    
    def get_metrics(self) -> BatchMetrics:
        """Get current metrics."""
        return self._metrics
    
    def get_progress(self) -> float:
        """Get current progress percentage."""
        return self._metrics.get_progress()
    
    def get_success_rate(self) -> float:
        """Get current success rate percentage."""
        return self._metrics.get_success_rate()
    
    def get_items_per_second(self) -> float:
        """Get current processing rate."""
        return self._metrics.items_per_second
    
    def get_estimated_remaining_time(self) -> Optional[timedelta]:
        """Get estimated remaining time."""
        return self._metrics.get_estimated_remaining_time()
    
    def complete(self) -> None:
        """Mark the batch as completed."""
        self._metrics.end_time = datetime.now()
        self._metrics.update_timing(end=self._metrics.end_time)
        
        if self.progress_bar:
            self.progress_bar.close()
        
        duration_s = (
            self._metrics.duration.total_seconds()
            if self._metrics.duration is not None
            else 0.0
        )
        self.logger.info(
            f"Batch completed: {self._metrics.processed_items}/{self._metrics.total_items} items "
            f"({self._metrics.get_success_rate():.1f}% success) in "
            f"{duration_s:.2f}s "
            f"({self._metrics.items_per_second:.1f} items/sec)"
        )
    
    def cancel(self) -> None:
        """Cancel the batch operation."""
        self._cancelled = True
        if self.progress_bar:
            self.progress_bar.close()
        self.logger.info("Batch operation cancelled")
    
    def is_cancelled(self) -> bool:
        """Check if the batch operation is cancelled."""
        return self._cancelled
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type:
            self.cancel()
        else:
            self.complete()


class ProgressBarFactory:
    """Factory for creating progress bars."""
    
    @staticmethod
    def create_progress_bar(
        total: int,
        desc: str = "Processing",
        unit: str = "items",
        **kwargs
    ) -> Optional[Any]:
        """
        Create a progress bar.
        
        Args:
            total: Total number of items
            desc: Description for the progress bar
            unit: Unit for the progress bar
            **kwargs: Additional arguments for tqdm
            
        Returns:
            Progress bar instance or None if tqdm not available
        """
        if not TQDM_AVAILABLE:
            logger.warning("tqdm not available - progress bar disabled")
            return None
        
        return tqdm(
            total=total,
            desc=desc,
            unit=unit,
            unit_scale=True,
            **kwargs
        )
    
    @staticmethod
    def create_async_progress_bar(
        total: int,
        desc: str = "Processing",
        unit: str = "items",
        **kwargs
    ) -> Optional[Any]:
        """
        Create an async progress bar.
        
        Args:
            total: Total number of items
            desc: Description for the progress bar
            unit: Unit for the progress bar
            **kwargs: Additional arguments for tqdm
            
        Returns:
            Async progress bar instance or None if tqdm not available
        """
        if not TQDM_AVAILABLE:
            logger.warning("tqdm not available - progress bar disabled")
            return None
        
        return tqdm(
            total=total,
            desc=desc,
            unit=unit,
            unit_scale=True,
            ascii=True,  # Better for async operations
            **kwargs
        )







