"""
Cache analytics and performance monitoring.

This module provides comprehensive analytics for cache performance,
including hit rates, response times, and usage patterns.
"""

from __future__ import annotations

from typing import Any, Dict, List
import time
import logging
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Container for cache performance metrics."""
    
    # Basic metrics
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    
    # Response times (in seconds)
    hit_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    miss_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    set_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    # Size metrics
    current_size: int = 0
    max_size: int = 0
    
    # Time-based metrics
    start_time: float = field(default_factory=time.time)
    last_reset: float = field(default_factory=time.time)
    
    @property
    def total_requests(self) -> int:
        """Total number of requests (hits + misses)."""
        return self.hits + self.misses
    
    @property
    def hit_rate(self) -> float:
        """Cache hit rate as a percentage."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests
    
    @property
    def miss_rate(self) -> float:
        """Cache miss rate as a percentage."""
        return 1.0 - self.hit_rate
    
    @property
    def avg_hit_time(self) -> float:
        """Average response time for cache hits."""
        if not self.hit_times:
            return 0.0
        return statistics.mean(self.hit_times)
    
    @property
    def avg_miss_time(self) -> float:
        """Average response time for cache misses."""
        if not self.miss_times:
            return 0.0
        return statistics.mean(self.miss_times)
    
    @property
    def avg_set_time(self) -> float:
        """Average response time for cache sets."""
        if not self.set_times:
            return 0.0
        return statistics.mean(self.set_times)
    
    @property
    def uptime(self) -> float:
        """Uptime in seconds."""
        return time.time() - self.start_time
    
    def reset(self):
        """Reset all metrics."""
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.errors = 0
        self.hit_times.clear()
        self.miss_times.clear()
        self.set_times.clear()
        self.last_reset = time.time()


class CacheAnalytics:
    """
    Comprehensive cache analytics and monitoring.
    
    This class provides detailed analytics for cache performance,
    including real-time metrics, historical data, and performance insights.
    """
    
    def __init__(self, max_history: int = 10000):
        """
        Initialize cache analytics.
        
        Args:
            max_history: Maximum number of historical data points
        """
        self.max_history = max_history
        
        # Current metrics
        self.metrics = CacheMetrics()
        
        # Historical data
        self.history: deque = deque(maxlen=max_history)
        
        # Per-endpoint metrics
        self.endpoint_metrics: Dict[str, CacheMetrics] = defaultdict(CacheMetrics)
        
        # Per-method metrics
        self.method_metrics: Dict[str, CacheMetrics] = defaultdict(CacheMetrics)
        
        # Performance alerts
        self.alerts: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            'hit_rate_min': 0.5,  # Alert if hit rate below 50%
            'avg_response_time_max': 0.1,  # Alert if avg response time > 100ms
            'error_rate_max': 0.05,  # Alert if error rate > 5%
        }
        
        logger.info("Cache analytics initialized")
    
    def record_hit(self, endpoint: str = "unknown", method: str = "unknown", response_time: float = 0.0):
        """
        Record a cache hit.
        
        Args:
            endpoint: Endpoint name
            method: Method name
            response_time: Response time in seconds
        """
        self.metrics.hits += 1
        self.metrics.hit_times.append(response_time)
        
        # Record per-endpoint metrics
        self.endpoint_metrics[endpoint].hits += 1
        self.endpoint_metrics[endpoint].hit_times.append(response_time)
        
        # Record per-method metrics
        self.method_metrics[method].hits += 1
        self.method_metrics[method].hit_times.append(response_time)
        
        # Check for alerts
        self._check_hit_rate_alert()
    
    def record_miss(self, endpoint: str = "unknown", method: str = "unknown", response_time: float = 0.0):
        """
        Record a cache miss.
        
        Args:
            endpoint: Endpoint name
            method: Method name
            response_time: Response time in seconds
        """
        self.metrics.misses += 1
        self.metrics.miss_times.append(response_time)
        
        # Record per-endpoint metrics
        self.endpoint_metrics[endpoint].misses += 1
        self.endpoint_metrics[endpoint].miss_times.append(response_time)
        
        # Record per-method metrics
        self.method_metrics[method].misses += 1
        self.method_metrics[method].miss_times.append(response_time)
        
        # Check for alerts
        self._check_hit_rate_alert()
    
    def record_set(self, endpoint: str = "unknown", method: str = "unknown", response_time: float = 0.0):
        """
        Record a cache set operation.
        
        Args:
            endpoint: Endpoint name
            method: Method name
            response_time: Response time in seconds
        """
        self.metrics.sets += 1
        self.metrics.set_times.append(response_time)
        
        # Record per-endpoint metrics
        self.endpoint_metrics[endpoint].sets += 1
        self.endpoint_metrics[endpoint].set_times.append(response_time)
        
        # Record per-method metrics
        self.method_metrics[method].sets += 1
        self.method_metrics[method].set_times.append(response_time)
    
    def record_delete(self, endpoint: str = "unknown", method: str = "unknown"):
        """
        Record a cache delete operation.
        
        Args:
            endpoint: Endpoint name
            method: Method name
        """
        self.metrics.deletes += 1
        
        # Record per-endpoint metrics
        self.endpoint_metrics[endpoint].deletes += 1
        
        # Record per-method metrics
        self.method_metrics[method].deletes += 1
    
    def record_error(self, endpoint: str = "unknown", method: str = "unknown", error: str = "unknown"):
        """
        Record a cache error.
        
        Args:
            endpoint: Endpoint name
            method: Method name
            error: Error description
        """
        self.metrics.errors += 1
        
        # Record per-endpoint metrics
        self.endpoint_metrics[endpoint].errors += 1
        
        # Record per-method metrics
        self.method_metrics[method].errors += 1
        
        # Check for error rate alerts
        self._check_error_rate_alert()
    
    def update_size(self, current_size: int, max_size: int):
        """
        Update cache size information.
        
        Args:
            current_size: Current cache size
            max_size: Maximum cache size
        """
        self.metrics.current_size = current_size
        self.metrics.max_size = max_size
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with detailed statistics
        """
        return {
            'overall': {
                'hits': self.metrics.hits,
                'misses': self.metrics.misses,
                'sets': self.metrics.sets,
                'deletes': self.metrics.deletes,
                'errors': self.metrics.errors,
                'total_requests': self.metrics.total_requests,
                'hit_rate': self.metrics.hit_rate,
                'miss_rate': self.metrics.miss_rate,
                'avg_hit_time': self.metrics.avg_hit_time,
                'avg_miss_time': self.metrics.avg_miss_time,
                'avg_set_time': self.metrics.avg_set_time,
                'current_size': self.metrics.current_size,
                'max_size': self.metrics.max_size,
                'size_ratio': self.metrics.current_size / self.metrics.max_size if self.metrics.max_size > 0 else 0,
                'uptime': self.metrics.uptime,
            },
            'by_endpoint': {
                endpoint: {
                    'hits': metrics.hits,
                    'misses': metrics.misses,
                    'hit_rate': metrics.hit_rate,
                    'avg_hit_time': metrics.avg_hit_time,
                    'avg_miss_time': metrics.avg_miss_time,
                }
                for endpoint, metrics in self.endpoint_metrics.items()
            },
            'by_method': {
                method: {
                    'hits': metrics.hits,
                    'misses': metrics.misses,
                    'hit_rate': metrics.hit_rate,
                    'avg_hit_time': metrics.avg_hit_time,
                    'avg_miss_time': metrics.avg_miss_time,
                }
                for method, metrics in self.method_metrics.items()
            },
            'alerts': self.alerts[-10:],  # Last 10 alerts
            'performance_score': self._calculate_performance_score(),
        }
    
    def get_performance_insights(self) -> List[str]:
        """
        Get performance insights and recommendations.
        
        Returns:
            List of insight messages
        """
        insights = []
        
        # Hit rate insights
        if self.metrics.hit_rate < 0.5:
            insights.append(f"Low hit rate ({self.metrics.hit_rate:.1%}). Consider increasing TTL or cache size.")
        elif self.metrics.hit_rate > 0.9:
            insights.append(f"Excellent hit rate ({self.metrics.hit_rate:.1%}). Cache is performing well.")
        
        # Response time insights
        if self.metrics.avg_hit_time > 0.01:  # 10ms
            insights.append(f"Slow cache hits ({self.metrics.avg_hit_time*1000:.1f}ms). Consider faster backend.")
        
        # Size insights
        if self.metrics.max_size > 0:
            size_ratio = self.metrics.current_size / self.metrics.max_size
            if size_ratio > 0.9:
                insights.append(f"Cache nearly full ({size_ratio:.1%}). Consider increasing size or TTL.")
            elif size_ratio < 0.1:
                insights.append(f"Cache underutilized ({size_ratio:.1%}). Consider decreasing size.")
        
        # Error insights
        if self.metrics.errors > 0:
            error_rate = self.metrics.errors / max(self.metrics.total_requests, 1)
            if error_rate > 0.01:  # 1%
                insights.append(f"High error rate ({error_rate:.1%}). Check cache backend health.")
        
        return insights
    
    def _calculate_performance_score(self) -> float:
        """
        Calculate overall performance score (0-100).
        
        Returns:
            Performance score
        """
        score = 0.0
        
        # Hit rate component (40% weight)
        hit_rate_score = min(self.metrics.hit_rate * 100, 100)
        score += hit_rate_score * 0.4
        
        # Response time component (30% weight)
        if self.metrics.avg_hit_time > 0:
            response_time_score = max(0, 100 - (self.metrics.avg_hit_time * 10000))  # Penalty for slow responses
            score += response_time_score * 0.3
        
        # Error rate component (20% weight)
        if self.metrics.total_requests > 0:
            error_rate = self.metrics.errors / self.metrics.total_requests
            error_score = max(0, 100 - (error_rate * 2000))  # Penalty for errors
            score += error_score * 0.2
        
        # Utilization component (10% weight)
        if self.metrics.max_size > 0:
            utilization = self.metrics.current_size / self.metrics.max_size
            utilization_score = min(utilization * 100, 100)
            score += utilization_score * 0.1
        
        return min(score, 100.0)
    
    def _check_hit_rate_alert(self):
        """Check for hit rate alerts."""
        if self.metrics.total_requests > 100:  # Only check after sufficient data
            if self.metrics.hit_rate < self.alert_thresholds['hit_rate_min']:
                self._add_alert('low_hit_rate', f"Hit rate below threshold: {self.metrics.hit_rate:.1%}")
    
    def _check_error_rate_alert(self):
        """Check for error rate alerts."""
        if self.metrics.total_requests > 100:  # Only check after sufficient data
            error_rate = self.metrics.errors / self.metrics.total_requests
            if error_rate > self.alert_thresholds['error_rate_max']:
                self._add_alert('high_error_rate', f"Error rate above threshold: {error_rate:.1%}")
    
    def _add_alert(self, alert_type: str, message: str):
        """Add a performance alert."""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': time.time(),
            'metrics': {
                'hit_rate': self.metrics.hit_rate,
                'total_requests': self.metrics.total_requests,
                'errors': self.metrics.errors,
            }
        }
        self.alerts.append(alert)
        logger.warning(f"Cache alert: {message}")
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics.reset()
        self.endpoint_metrics.clear()
        self.method_metrics.clear()
        self.alerts.clear()
        logger.info("Cache metrics reset")
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Export metrics in specified format.
        
        Args:
            format: Export format ('json', 'csv')
            
        Returns:
            Exported metrics as string
        """
        if format == "json":
            import json
            return json.dumps(self.get_stats(), indent=2)
        elif format == "csv":
            # Simple CSV export
            stats = self.get_stats()
            lines = ["metric,value"]
            for key, value in stats['overall'].items():
                lines.append(f"{key},{value}")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_historical_data(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get historical performance data.
        
        Args:
            hours: Number of hours of data to return
            
        Returns:
            List of historical data points
        """
        cutoff_time = time.time() - (hours * 3600)
        return [
            data for data in self.history
            if data.get('timestamp', 0) > cutoff_time
        ]







