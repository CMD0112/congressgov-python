"""Memory monitoring for batch operations, to catch out-of-memory conditions before they hit."""

from __future__ import annotations

from typing import Dict, Optional, List, Any
import logging
import gc
import time
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """Tracks current/peak memory usage and triggers garbage collection when needed.

    Example:
        monitor = MemoryMonitor()
        
        # Check current memory usage
        usage = monitor.get_memory_usage_mb()
        
        # Get detailed memory stats
        stats = monitor.get_memory_stats()
        
        # Force garbage collection if needed
        if usage > 1000:  # 1GB
            monitor.force_gc()
    """
    
    def __init__(self, process: Optional[Any] = None):
        """
        Initialize the memory monitor.
        
        Args:
            process: psutil Process object (uses current process if None)
        """
        self.process = process
        if self.process is None and PSUTIL_AVAILABLE:
            self.process = psutil.Process()
        
        self._peak_memory_mb = 0.0
        self._gc_count = 0
        self._last_gc_time = None
        self._memory_history: List[Dict[str, Any]] = []
        self._max_history = 1000  # Keep last 1000 measurements
    
    def get_memory_usage_mb(self) -> float:
        """
        Get current memory usage in MB.
        
        Returns:
            Current memory usage in MB
        """
        if not PSUTIL_AVAILABLE or not self.process:
            # Fallback to basic memory info
            try:
                import resource
                usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                return usage / 1024.0  # Convert KB to MB
            except (ImportError, OSError):
                return 0.0
        
        try:
            memory_info = self.process.memory_info()
            usage_mb = memory_info.rss / 1024.0 / 1024.0  # Convert bytes to MB
            
            # Update peak memory
            if usage_mb > self._peak_memory_mb:
                self._peak_memory_mb = usage_mb
            
            # Record in history
            self._record_memory_usage(usage_mb)
            
            return usage_mb
            
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return 0.0
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Return current/peak/available memory usage as a dict."""
        current_usage = self.get_memory_usage_mb()
        
        stats = {
            'current_mb': current_usage,
            'peak_mb': self._peak_memory_mb,
            'gc_count': self._gc_count,
            'last_gc_time': self._last_gc_time.isoformat() if self._last_gc_time else None,
            'history_count': len(self._memory_history)
        }
        
        if PSUTIL_AVAILABLE and self.process:
            try:
                memory_info = self.process.memory_info()
                memory_percent = self.process.memory_percent()
                
                stats.update({
                    'rss_mb': memory_info.rss / 1024.0 / 1024.0,
                    'vms_mb': memory_info.vms / 1024.0 / 1024.0,
                    'percent': memory_percent,
                    'available_mb': psutil.virtual_memory().available / 1024.0 / 1024.0,
                    'total_mb': psutil.virtual_memory().total / 1024.0 / 1024.0
                })
            except Exception as e:
                logger.warning(f"Failed to get detailed memory stats: {e}")
        
        return stats
    
    def get_memory_trend(self, window_size: int = 10) -> Dict[str, Any]:
        """
        Get memory usage trend over recent measurements.
        
        Args:
            window_size: Number of recent measurements to analyze
            
        Returns:
            Dictionary with trend information
        """
        if len(self._memory_history) < 2:
            return {'trend': 'insufficient_data', 'change_mb': 0.0, 'change_percent': 0.0}
        
        # Get recent measurements
        recent = self._memory_history[-window_size:]
        if len(recent) < 2:
            return {'trend': 'insufficient_data', 'change_mb': 0.0, 'change_percent': 0.0}
        
        # Calculate trend
        first_usage = recent[0]['usage_mb']
        last_usage = recent[-1]['usage_mb']
        change_mb = last_usage - first_usage
        change_percent = (change_mb / first_usage) * 100.0 if first_usage > 0 else 0.0
        
        # Determine trend direction
        if abs(change_percent) < 1.0:
            trend = 'stable'
        elif change_percent > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        return {
            'trend': trend,
            'change_mb': change_mb,
            'change_percent': change_percent,
            'window_size': len(recent),
            'first_usage_mb': first_usage,
            'last_usage_mb': last_usage
        }
    
    def force_gc(self) -> Dict[str, Any]:
        """
        Force garbage collection and return statistics.
        
        Returns:
            Dictionary with GC statistics
        """
        start_time = time.time()
        start_usage = self.get_memory_usage_mb()
        
        # Force garbage collection
        collected = gc.collect()
        
        end_time = time.time()
        end_usage = self.get_memory_usage_mb()
        
        # Update GC statistics
        self._gc_count += 1
        self._last_gc_time = datetime.now()
        
        gc_stats = {
            'collected_objects': collected,
            'memory_freed_mb': start_usage - end_usage,
            'gc_time_seconds': end_time - start_time,
            'total_gc_count': self._gc_count,
            'gc_timestamp': self._last_gc_time.isoformat()
        }
        
        logger.debug(f"Garbage collection: {collected} objects collected, "
                    f"{gc_stats['memory_freed_mb']:.2f}MB freed")
        
        return gc_stats
    
    def should_force_gc(self, threshold_mb: float = 100.0) -> bool:
        """
        Check if garbage collection should be forced.
        
        Args:
            threshold_mb: Memory threshold in MB
            
        Returns:
            True if GC should be forced
        """
        current_usage = self.get_memory_usage_mb()
        return current_usage > threshold_mb
    
    def get_memory_pressure(self) -> str:
        """
        Get current memory pressure level.
        
        Returns:
            Memory pressure level: 'low', 'medium', 'high', 'critical'
        """
        if not PSUTIL_AVAILABLE:
            return 'unknown'
        
        try:
            memory = psutil.virtual_memory()
            percent = memory.percent
            
            if percent < 50:
                return 'low'
            elif percent < 75:
                return 'medium'
            elif percent < 90:
                return 'high'
            else:
                return 'critical'
        except Exception as e:
            logger.warning(f"Failed to get memory pressure: {e}")
            return 'unknown'
    
    def get_recommended_batch_size(
        self,
        current_batch_size: int,
        max_memory_mb: float,
        safety_factor: float = 0.8
    ) -> int:
        """
        Get recommended batch size based on current memory usage.
        
        Args:
            current_batch_size: Current batch size
            max_memory_mb: Maximum allowed memory usage
            safety_factor: Safety factor (0.0-1.0)
            
        Returns:
            Recommended batch size
        """
        current_usage = self.get_memory_usage_mb()
        available_memory = max_memory_mb * safety_factor - current_usage
        
        if available_memory <= 0:
            return 1  # Minimum batch size
        
        # Estimate memory per item (rough heuristic)
        if len(self._memory_history) >= 2:
            # Calculate memory growth rate
            recent = self._memory_history[-10:]
            if len(recent) >= 2:
                memory_growth = recent[-1]['usage_mb'] - recent[0]['usage_mb']
                items_processed = recent[-1]['timestamp'] - recent[0]['timestamp']
                if items_processed > 0:
                    memory_per_item = memory_growth / items_processed
                    if memory_per_item > 0:
                        recommended_size = int(available_memory / memory_per_item)
                        return max(1, min(recommended_size, current_batch_size * 2))
        
        # Fallback: reduce batch size if memory usage is high
        if current_usage > max_memory_mb * 0.8:
            return max(1, current_batch_size // 2)
        elif current_usage < max_memory_mb * 0.5:
            return min(current_batch_size * 2, current_batch_size * 4)
        else:
            return current_batch_size
    
    def _record_memory_usage(self, usage_mb: float) -> None:
        """Record memory usage in history."""
        record = {
            'timestamp': len(self._memory_history),
            'usage_mb': usage_mb,
            'time': datetime.now()
        }
        
        self._memory_history.append(record)
        
        # Keep only recent history
        if len(self._memory_history) > self._max_history:
            self._memory_history = self._memory_history[-self._max_history:]
    
    def clear_history(self) -> None:
        """Clear memory usage history."""
        self._memory_history.clear()
        logger.debug("Memory usage history cleared")
    
    def get_history_summary(self) -> Dict[str, Any]:
        """Get summary of memory usage history."""
        if not self._memory_history:
            return {'count': 0, 'min_mb': 0.0, 'max_mb': 0.0, 'avg_mb': 0.0}
        
        usages = [record['usage_mb'] for record in self._memory_history]
        
        return {
            'count': len(usages),
            'min_mb': min(usages),
            'max_mb': max(usages),
            'avg_mb': sum(usages) / len(usages),
            'first_measurement': self._memory_history[0]['time'].isoformat(),
            'last_measurement': self._memory_history[-1]['time'].isoformat()
        }


class MemoryAwareProcessor:
    """
    Mixin class for processors that need memory awareness.
    
    This class provides memory monitoring capabilities that can be mixed into
    other processor classes.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize with memory monitoring."""
        super().__init__(*args, **kwargs)
        self.memory_monitor = MemoryMonitor()
        self._memory_check_interval = 100  # Check every 100 items
        self._items_since_memory_check = 0
    
    def _check_memory_usage(self, max_memory_mb: Optional[float] = None) -> bool:
        """
        Check memory usage and take action if needed.
        
        Args:
            max_memory_mb: Maximum allowed memory usage
            
        Returns:
            True if processing should continue, False if memory limit exceeded
        """
        self._items_since_memory_check += 1
        
        if self._items_since_memory_check < self._memory_check_interval:
            return True
        
        self._items_since_memory_check = 0
        
        if max_memory_mb:
            current_usage = self.memory_monitor.get_memory_usage_mb()
            if current_usage > max_memory_mb:
                logger.warning(f"Memory usage {current_usage:.1f}MB exceeds limit {max_memory_mb}MB")
                
                # Try garbage collection
                self.memory_monitor.force_gc()
                new_usage = self.memory_monitor.get_memory_usage_mb()
                
                if new_usage > max_memory_mb:
                    logger.error(f"Memory limit exceeded even after GC: {new_usage:.1f}MB")
                    return False
                else:
                    logger.info(f"Memory usage reduced to {new_usage:.1f}MB after GC")
        
        return True
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics."""
        return self.memory_monitor.get_memory_stats()







