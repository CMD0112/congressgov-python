"""Rate limiting metrics, alerting, and performance analysis."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
import time
import logging
from dataclasses import dataclass, field
from collections import deque, defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class RateLimitAlert:
    """Rate limiting alert."""
    
    level: AlertLevel
    message: str
    timestamp: float
    endpoint: str
    metrics: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitMetrics:
    """Rate limiting metrics for an endpoint."""
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    
    # Timing metrics
    total_delay_time: float = 0.0
    avg_delay_time: float = 0.0
    max_delay_time: float = 0.0
    
    # Rate metrics
    current_rate: float = 0.0
    peak_rate: float = 0.0
    avg_rate: float = 0.0
    
    # Error metrics
    consecutive_errors: int = 0
    max_consecutive_errors: int = 0
    
    # Time tracking
    window_start: float = field(default_factory=time.time)
    last_request_time: float = 0.0
    
    def update_rate(self, current_time: float):
        """Update rate calculations."""
        if current_time - self.window_start >= 1.0:  # 1 second window
            self.current_rate = self.total_requests / (current_time - self.window_start)
            self.peak_rate = max(self.peak_rate, self.current_rate)
            self.avg_rate = (self.avg_rate + self.current_rate) / 2
            self.total_requests = 0
            self.window_start = current_time


class RateLimitMonitor:
    """Tracks rate limiting metrics per endpoint and fires alerts when thresholds are crossed."""
    
    def __init__(
        self,
        alert_callbacks: Optional[List[Callable[[RateLimitAlert], None]]] = None,
        metrics_window: int = 1000
    ):
        """
        Initialize rate limit monitor.
        
        Args:
            alert_callbacks: List of alert callback functions
            metrics_window: Number of data points to keep in memory
        """
        self.alert_callbacks = alert_callbacks or []
        self.metrics_window = metrics_window
        
        # Per-endpoint metrics
        self.endpoint_metrics: Dict[str, RateLimitMetrics] = defaultdict(RateLimitMetrics)
        
        # Historical data
        self.historical_data: deque = deque(maxlen=metrics_window)
        
        # Alert thresholds
        self.thresholds = {
            'high_error_rate': 0.1,  # 10% error rate
            'high_delay_time': 5.0,  # 5 seconds average delay
            'low_success_rate': 0.8,  # 80% success rate
            'high_consecutive_errors': 5,  # 5 consecutive errors
        }
        
        # Alert history
        self.alerts: List[RateLimitAlert] = []
        self.max_alerts = 1000
        
        logger.info("Rate limit monitor initialized")
    
    def record_request(
        self,
        endpoint: str,
        success: bool,
        delay_time: float = 0.0,
        was_rate_limited: bool = False,
        error: Optional[str] = None
    ):
        """
        Record a request for monitoring.
        
        Args:
            endpoint: Endpoint identifier
            success: Whether the request was successful
            delay_time: Time spent waiting for rate limit
            was_rate_limited: Whether the request was rate limited
            error: Error message if request failed
        """
        current_time = time.time()
        metrics = self.endpoint_metrics[endpoint]
        
        # Update basic metrics
        metrics.total_requests += 1
        metrics.last_request_time = current_time
        
        if success:
            metrics.successful_requests += 1
            metrics.consecutive_errors = 0
        else:
            metrics.failed_requests += 1
            metrics.consecutive_errors += 1
            metrics.max_consecutive_errors = max(
                metrics.max_consecutive_errors,
                metrics.consecutive_errors
            )
        
        if was_rate_limited:
            metrics.rate_limited_requests += 1
        
        # Update timing metrics
        if delay_time > 0:
            metrics.total_delay_time += delay_time
            metrics.avg_delay_time = metrics.total_delay_time / metrics.total_requests
            metrics.max_delay_time = max(metrics.max_delay_time, delay_time)
        
        # Update rate calculations
        metrics.update_rate(current_time)
        
        # Record historical data
        self.historical_data.append({
            'timestamp': current_time,
            'endpoint': endpoint,
            'success': success,
            'delay_time': delay_time,
            'was_rate_limited': was_rate_limited,
            'error': error,
        })
        
        # Check for alerts
        self._check_alerts(endpoint, metrics, current_time)
    
    def _check_alerts(self, endpoint: str, metrics: RateLimitMetrics, current_time: float):
        """Check for alert conditions."""
        # High error rate alert
        if metrics.total_requests > 10:  # Need sufficient data
            error_rate = metrics.failed_requests / metrics.total_requests
            if error_rate > self.thresholds['high_error_rate']:
                self._create_alert(
                    AlertLevel.WARNING,
                    f"High error rate for {endpoint}: {error_rate:.1%}",
                    endpoint,
                    metrics,
                    {'error_rate': error_rate}
                )
        
        # High delay time alert
        if metrics.avg_delay_time > self.thresholds['high_delay_time']:
            self._create_alert(
                AlertLevel.WARNING,
                f"High delay time for {endpoint}: {metrics.avg_delay_time:.2f}s",
                endpoint,
                metrics,
                {'avg_delay_time': metrics.avg_delay_time}
            )
        
        # Low success rate alert
        if metrics.total_requests > 10:  # Need sufficient data
            success_rate = metrics.successful_requests / metrics.total_requests
            if success_rate < self.thresholds['low_success_rate']:
                self._create_alert(
                    AlertLevel.ERROR,
                    f"Low success rate for {endpoint}: {success_rate:.1%}",
                    endpoint,
                    metrics,
                    {'success_rate': success_rate}
                )
        
        # High consecutive errors alert
        if metrics.consecutive_errors >= self.thresholds['high_consecutive_errors']:
            self._create_alert(
                AlertLevel.CRITICAL,
                f"High consecutive errors for {endpoint}: {metrics.consecutive_errors}",
                endpoint,
                metrics,
                {'consecutive_errors': metrics.consecutive_errors}
            )
    
    def _create_alert(
        self,
        level: AlertLevel,
        message: str,
        endpoint: str,
        metrics: RateLimitMetrics,
        context: Dict[str, Any]
    ):
        """Create and process an alert."""
        alert = RateLimitAlert(
            level=level,
            message=message,
            timestamp=time.time(),
            endpoint=endpoint,
            metrics={
                'total_requests': metrics.total_requests,
                'successful_requests': metrics.successful_requests,
                'failed_requests': metrics.failed_requests,
                'rate_limited_requests': metrics.rate_limited_requests,
                'avg_delay_time': metrics.avg_delay_time,
                'current_rate': metrics.current_rate,
                'consecutive_errors': metrics.consecutive_errors,
            },
            context=context
        )
        
        # Add to alert history
        self.alerts.append(alert)
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        # Log alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL,
        }[level]
        
        logger.log(log_level, f"Rate limit alert: {message}")
    
    def get_metrics(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for an endpoint or all endpoints.
        
        Args:
            endpoint: Specific endpoint (None for all)
            
        Returns:
            Metrics dictionary
        """
        if endpoint:
            if endpoint not in self.endpoint_metrics:
                return {}
            
            metrics = self.endpoint_metrics[endpoint]
            return {
                'endpoint': endpoint,
                'total_requests': metrics.total_requests,
                'successful_requests': metrics.successful_requests,
                'failed_requests': metrics.failed_requests,
                'rate_limited_requests': metrics.rate_limited_requests,
                'success_rate': metrics.successful_requests / max(metrics.total_requests, 1),
                'error_rate': metrics.failed_requests / max(metrics.total_requests, 1),
                'rate_limit_rate': metrics.rate_limited_requests / max(metrics.total_requests, 1),
                'avg_delay_time': metrics.avg_delay_time,
                'max_delay_time': metrics.max_delay_time,
                'current_rate': metrics.current_rate,
                'peak_rate': metrics.peak_rate,
                'avg_rate': metrics.avg_rate,
                'consecutive_errors': metrics.consecutive_errors,
                'max_consecutive_errors': metrics.max_consecutive_errors,
            }
        else:
            # Return metrics for all endpoints
            return {
                endpoint: self.get_metrics(endpoint)
                for endpoint in self.endpoint_metrics.keys()
            }
    
    def get_alerts(
        self,
        level: Optional[AlertLevel] = None,
        endpoint: Optional[str] = None,
        limit: int = 100
    ) -> List[RateLimitAlert]:
        """
        Get recent alerts.
        
        Args:
            level: Filter by alert level
            endpoint: Filter by endpoint
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        alerts = self.alerts
        
        # Apply filters
        if level:
            alerts = [alert for alert in alerts if alert.level == level]
        
        if endpoint:
            alerts = [alert for alert in alerts if alert.endpoint == endpoint]
        
        # Return most recent alerts
        return alerts[-limit:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get overall performance summary.
        
        Returns:
            Performance summary dictionary
        """
        if not self.endpoint_metrics:
            return {}
        
        # Aggregate metrics across all endpoints
        total_requests = sum(m.total_requests for m in self.endpoint_metrics.values())
        total_successful = sum(m.successful_requests for m in self.endpoint_metrics.values())
        total_failed = sum(m.failed_requests for m in self.endpoint_metrics.values())
        total_rate_limited = sum(m.rate_limited_requests for m in self.endpoint_metrics.values())
        total_delay_time = sum(m.total_delay_time for m in self.endpoint_metrics.values())
        
        # Calculate rates
        success_rate = total_successful / max(total_requests, 1)
        error_rate = total_failed / max(total_requests, 1)
        rate_limit_rate = total_rate_limited / max(total_requests, 1)
        avg_delay_time = total_delay_time / max(total_requests, 1)
        
        # Get recent alerts
        recent_alerts = self.get_alerts(limit=10)
        critical_alerts = self.get_alerts(level=AlertLevel.CRITICAL, limit=5)
        
        return {
            'overall': {
                'total_requests': total_requests,
                'successful_requests': total_successful,
                'failed_requests': total_failed,
                'rate_limited_requests': total_rate_limited,
                'success_rate': success_rate,
                'error_rate': error_rate,
                'rate_limit_rate': rate_limit_rate,
                'avg_delay_time': avg_delay_time,
            },
            'endpoints': len(self.endpoint_metrics),
            'recent_alerts': len(recent_alerts),
            'critical_alerts': len(critical_alerts),
            'performance_score': self._calculate_performance_score(),
        }
    
    def _calculate_performance_score(self) -> float:
        """
        Calculate overall performance score (0-100).
        
        Returns:
            Performance score
        """
        if not self.endpoint_metrics:
            return 100.0
        
        # Aggregate metrics
        total_requests = sum(m.total_requests for m in self.endpoint_metrics.values())
        total_successful = sum(m.successful_requests for m in self.endpoint_metrics.values())
        total_delay_time = sum(m.total_delay_time for m in self.endpoint_metrics.values())
        
        if total_requests == 0:
            return 100.0
        
        # Calculate components
        success_rate = total_successful / total_requests
        avg_delay_time = total_delay_time / total_requests
        
        # Score based on success rate (70% weight)
        success_score = success_rate * 100 * 0.7
        
        # Score based on delay time (30% weight)
        # Penalty for delays > 1 second
        delay_penalty = max(0, (avg_delay_time - 1.0) * 20)
        delay_score = max(0, 100 - delay_penalty) * 0.3
        
        return min(success_score + delay_score, 100.0)
    
    def add_alert_callback(self, callback: Callable[[RateLimitAlert], None]):
        """
        Add an alert callback function.
        
        Args:
            callback: Function to call when alerts are generated
        """
        self.alert_callbacks.append(callback)
    
    def set_threshold(self, name: str, value: float):
        """
        Set an alert threshold.
        
        Args:
            name: Threshold name
            value: Threshold value
        """
        if name in self.thresholds:
            self.thresholds[name] = value
            logger.info(f"Updated threshold {name} to {value}")
        else:
            logger.warning(f"Unknown threshold: {name}")
    
    def reset_metrics(self, endpoint: Optional[str] = None):
        """
        Reset metrics for an endpoint or all endpoints.
        
        Args:
            endpoint: Specific endpoint (None for all)
        """
        if endpoint:
            if endpoint in self.endpoint_metrics:
                del self.endpoint_metrics[endpoint]
                logger.info(f"Reset metrics for endpoint: {endpoint}")
        else:
            self.endpoint_metrics.clear()
            self.historical_data.clear()
            self.alerts.clear()
            logger.info("Reset all metrics")
    
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
            return json.dumps(self.get_performance_summary(), indent=2)
        elif format == "csv":
            # Simple CSV export
            summary = self.get_performance_summary()
            lines = ["metric,value"]
            for key, value in summary['overall'].items():
                lines.append(f"{key},{value}")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")


# Convenience functions for common monitoring tasks
def create_console_alert_callback() -> Callable[[RateLimitAlert], None]:
    """Create a console alert callback."""
    def callback(alert: RateLimitAlert):
        print(f"[{alert.level.value.upper()}] {alert.timestamp}: {alert.message}")
    
    return callback


def create_logging_alert_callback() -> Callable[[RateLimitAlert], None]:
    """Create a logging alert callback."""
    def callback(alert: RateLimitAlert):
        level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL,
        }[alert.level]
        
        logger.log(level, f"Rate limit alert: {alert.message}")
    
    return callback







