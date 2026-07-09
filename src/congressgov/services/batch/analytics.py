"""Analyzes batch processing performance: bottleneck identification and optimization recommendations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import deque
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceSnapshot:
    """Snapshot of performance at a specific point in time."""
    
    timestamp: datetime
    items_processed: int
    items_per_second: float
    memory_usage_mb: float
    error_count: int
    api_calls_made: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'items_processed': self.items_processed,
            'items_per_second': self.items_per_second,
            'memory_usage_mb': self.memory_usage_mb,
            'error_count': self.error_count,
            'api_calls_made': self.api_calls_made
        }


@dataclass
class BottleneckAnalysis:
    """Analysis of performance bottlenecks."""
    
    bottleneck_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    recommendation: str
    impact_percentage: float
    affected_metrics: List[str]


@dataclass
class OptimizationRecommendation:
    """Recommendation for optimizing batch processing."""
    
    category: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    title: str
    description: str
    expected_improvement: str
    implementation_effort: str
    metrics_affected: List[str]


class BatchAnalytics:
    """Analyzes batch processing performance: tracking, bottleneck
    identification, and optimization recommendations.

    Example:
        analytics = BatchAnalytics()
        
        # Record performance snapshots
        analytics.record_snapshot(items_processed=100, items_per_second=50.0)
        
        # Analyze performance
        analysis = analytics.analyze_performance()
        
        # Get optimization recommendations
        recommendations = analytics.get_optimization_recommendations()
    """
    
    def __init__(
        self,
        max_snapshots: int = 1000,
        analysis_window: int = 100,  # Analyze last 100 snapshots
        performance_thresholds: Optional[Dict[str, float]] = None
    ):
        """
        Initialize the batch analytics.
        
        Args:
            max_snapshots: Maximum number of snapshots to keep
            analysis_window: Number of recent snapshots to analyze
            performance_thresholds: Custom performance thresholds
        """
        self.max_snapshots = max_snapshots
        self.analysis_window = analysis_window
        self.performance_thresholds = performance_thresholds or {
            'min_items_per_second': 10.0,
            'max_memory_usage_mb': 1000.0,
            'max_error_rate': 0.05,  # 5%
            'min_success_rate': 0.95  # 95%
        }
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self._snapshots: deque = deque(maxlen=max_snapshots)
        self._error_history: List[Tuple[datetime, str]] = []
        self._performance_history: List[Dict[str, Any]] = []
        
        # Analysis cache
        self._last_analysis_time: Optional[datetime] = None
        self._cached_analysis: Optional[Dict[str, Any]] = None
    
    def record_snapshot(
        self,
        items_processed: int,
        items_per_second: float,
        memory_usage_mb: float = 0.0,
        error_count: int = 0,
        api_calls_made: int = 0
    ) -> None:
        """
        Record a performance snapshot.
        
        Args:
            items_processed: Number of items processed
            items_per_second: Current processing rate
            memory_usage_mb: Current memory usage in MB
            error_count: Number of errors encountered
            api_calls_made: Number of API calls made
        """
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            items_processed=items_processed,
            items_per_second=items_per_second,
            memory_usage_mb=memory_usage_mb,
            error_count=error_count,
            api_calls_made=api_calls_made
        )
        
        self._snapshots.append(snapshot)
        self.logger.debug(f"Recorded performance snapshot: {items_processed} items, {items_per_second:.1f} items/sec")
    
    def record_error(self, error_type: str) -> None:
        """
        Record an error occurrence.
        
        Args:
            error_type: Type of error that occurred
        """
        self._error_history.append((datetime.now(), error_type))
        self.logger.debug(f"Recorded error: {error_type}")
    
    def analyze_performance(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Analyze performance and identify bottlenecks.
        
        Args:
            force_refresh: Force refresh of cached analysis
            
        Returns:
            Dictionary with performance analysis
        """
        # Check if we need to refresh the analysis
        if (not force_refresh and 
            self._cached_analysis and 
            self._last_analysis_time and 
            datetime.now() - self._last_analysis_time < timedelta(seconds=30)):
            return self._cached_analysis
        
        if len(self._snapshots) < 2:
            return {'status': 'insufficient_data', 'message': 'Not enough snapshots for analysis'}
        
        # Get recent snapshots for analysis
        recent_snapshots = list(self._snapshots)[-self.analysis_window:]
        
        # Calculate basic metrics
        analysis = self._calculate_basic_metrics(recent_snapshots)
        
        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(recent_snapshots)
        analysis['bottlenecks'] = [b.__dict__ for b in bottlenecks]
        
        # Calculate trends
        trends = self._calculate_trends(recent_snapshots)
        analysis['trends'] = trends
        
        # Calculate efficiency metrics
        efficiency = self._calculate_efficiency_metrics(recent_snapshots)
        analysis['efficiency'] = efficiency
        
        # Cache the analysis
        self._cached_analysis = analysis
        self._last_analysis_time = datetime.now()
        
        return analysis
    
    def _calculate_basic_metrics(self, snapshots: List[PerformanceSnapshot]) -> Dict[str, Any]:
        """Calculate basic performance metrics."""
        if not snapshots:
            return {}
        
        items_per_second_values = [s.items_per_second for s in snapshots]
        memory_values = [s.memory_usage_mb for s in snapshots]
        error_counts = [s.error_count for s in snapshots]
        
        return {
            'avg_items_per_second': statistics.mean(items_per_second_values),
            'max_items_per_second': max(items_per_second_values),
            'min_items_per_second': min(items_per_second_values),
            'std_items_per_second': statistics.stdev(items_per_second_values) if len(items_per_second_values) > 1 else 0,
            'avg_memory_usage_mb': statistics.mean(memory_values),
            'max_memory_usage_mb': max(memory_values),
            'total_errors': sum(error_counts),
            'error_rate': sum(error_counts) / len(snapshots),
            'snapshot_count': len(snapshots),
            'time_span_seconds': (snapshots[-1].timestamp - snapshots[0].timestamp).total_seconds()
        }
    
    def _identify_bottlenecks(self, snapshots: List[PerformanceSnapshot]) -> List[BottleneckAnalysis]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        if not snapshots:
            return bottlenecks
        
        # Check processing rate bottleneck
        avg_rate = statistics.mean([s.items_per_second for s in snapshots])
        if avg_rate < self.performance_thresholds['min_items_per_second']:
            bottlenecks.append(BottleneckAnalysis(
                bottleneck_type='processing_rate',
                severity='high' if avg_rate < self.performance_thresholds['min_items_per_second'] * 0.5 else 'medium',
                description=f"Low processing rate: {avg_rate:.1f} items/sec",
                recommendation="Consider increasing concurrency or optimizing the processing function",
                impact_percentage=100.0 - (avg_rate / self.performance_thresholds['min_items_per_second'] * 100),
                affected_metrics=['items_per_second']
            ))
        
        # Check memory bottleneck
        max_memory = max([s.memory_usage_mb for s in snapshots])
        if max_memory > self.performance_thresholds['max_memory_usage_mb']:
            bottlenecks.append(BottleneckAnalysis(
                bottleneck_type='memory_usage',
                severity='critical' if max_memory > self.performance_thresholds['max_memory_usage_mb'] * 1.5 else 'high',
                description=f"High memory usage: {max_memory:.1f} MB",
                recommendation="Consider reducing batch size or implementing streaming processing",
                impact_percentage=((max_memory - self.performance_thresholds['max_memory_usage_mb']) / 
                                 self.performance_thresholds['max_memory_usage_mb'] * 100),
                affected_metrics=['memory_usage_mb']
            ))
        
        # Check error rate bottleneck
        total_errors = sum([s.error_count for s in snapshots])
        error_rate = total_errors / len(snapshots)
        if error_rate > self.performance_thresholds['max_error_rate']:
            bottlenecks.append(BottleneckAnalysis(
                bottleneck_type='error_rate',
                severity='high' if error_rate > self.performance_thresholds['max_error_rate'] * 2 else 'medium',
                description=f"High error rate: {error_rate:.2%}",
                recommendation="Review error handling and retry logic",
                impact_percentage=((error_rate - self.performance_thresholds['max_error_rate']) / 
                                 self.performance_thresholds['max_error_rate'] * 100),
                affected_metrics=['error_count']
            ))
        
        return bottlenecks
    
    def _calculate_trends(self, snapshots: List[PerformanceSnapshot]) -> Dict[str, Any]:
        """Calculate performance trends."""
        if len(snapshots) < 3:
            return {'status': 'insufficient_data'}
        
        # Calculate trend for items per second
        rates = [s.items_per_second for s in snapshots]
        rate_trend = self._calculate_trend_direction(rates)
        
        # Calculate trend for memory usage
        memory_values = [s.memory_usage_mb for s in snapshots]
        memory_trend = self._calculate_trend_direction(memory_values)
        
        # Calculate trend for error count
        error_counts = [s.error_count for s in snapshots]
        error_trend = self._calculate_trend_direction(error_counts)
        
        return {
            'processing_rate_trend': rate_trend,
            'memory_usage_trend': memory_trend,
            'error_count_trend': error_trend,
            'overall_trend': self._calculate_overall_trend(rate_trend, memory_trend, error_trend)
        }
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate the direction of a trend."""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        y = values
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_overall_trend(self, rate_trend: str, memory_trend: str, error_trend: str) -> str:
        """Calculate overall trend from individual trends."""
        
        # Weight the trends (rate is most important, errors are bad)
        if rate_trend == 'increasing' and error_trend != 'increasing':
            return 'improving'
        elif rate_trend == 'decreasing' or error_trend == 'increasing':
            return 'degrading'
        else:
            return 'stable'
    
    def _calculate_efficiency_metrics(self, snapshots: List[PerformanceSnapshot]) -> Dict[str, Any]:
        """Calculate efficiency metrics."""
        if not snapshots:
            return {}
        
        # Calculate resource utilization
        total_items = snapshots[-1].items_processed - snapshots[0].items_processed
        total_time = (snapshots[-1].timestamp - snapshots[0].timestamp).total_seconds()
        total_api_calls = sum([s.api_calls_made for s in snapshots])
        
        return {
            'items_per_second': total_items / total_time if total_time > 0 else 0,
            'api_calls_per_item': total_api_calls / total_items if total_items > 0 else 0,
            'memory_efficiency': self._calculate_memory_efficiency(snapshots),
            'error_efficiency': self._calculate_error_efficiency(snapshots)
        }
    
    def _calculate_memory_efficiency(self, snapshots: List[PerformanceSnapshot]) -> float:
        """Calculate memory efficiency score (0-1, higher is better)."""
        if not snapshots:
            return 0.0
        
        memory_values = [s.memory_usage_mb for s in snapshots]
        avg_memory = statistics.mean(memory_values)
        max_memory = max(memory_values)
        
        # Efficiency based on how close average is to max (more stable = better)
        if max_memory == 0:
            return 1.0
        
        stability = 1.0 - (max_memory - avg_memory) / max_memory
        return max(0.0, min(1.0, stability))
    
    def _calculate_error_efficiency(self, snapshots: List[PerformanceSnapshot]) -> float:
        """Calculate error efficiency score (0-1, higher is better)."""
        if not snapshots:
            return 1.0
        
        total_errors = sum([s.error_count for s in snapshots])
        total_items = snapshots[-1].items_processed - snapshots[0].items_processed
        
        if total_items == 0:
            return 1.0
        
        error_rate = total_errors / total_items
        return max(0.0, 1.0 - error_rate)
    
    def get_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """Get optimization recommendations based on analysis."""
        analysis = self.analyze_performance()
        recommendations = []
        
        # Check for processing rate issues
        if 'avg_items_per_second' in analysis:
            avg_rate = analysis['avg_items_per_second']
            if avg_rate < self.performance_thresholds['min_items_per_second']:
                recommendations.append(OptimizationRecommendation(
                    category='performance',
                    priority='high',
                    title='Increase Processing Concurrency',
                    description=f"Current rate of {avg_rate:.1f} items/sec is below threshold",
                    expected_improvement='2-5x faster processing',
                    implementation_effort='low',
                    metrics_affected=['items_per_second']
                ))
        
        # Check for memory issues
        if 'max_memory_usage_mb' in analysis:
            max_memory = analysis['max_memory_usage_mb']
            if max_memory > self.performance_thresholds['max_memory_usage_mb']:
                recommendations.append(OptimizationRecommendation(
                    category='memory',
                    priority='critical',
                    title='Implement Streaming Processing',
                    description=f"Memory usage of {max_memory:.1f} MB exceeds threshold",
                    expected_improvement='70% memory reduction',
                    implementation_effort='medium',
                    metrics_affected=['memory_usage_mb']
                ))
        
        # Check for error issues
        if 'error_rate' in analysis:
            error_rate = analysis['error_rate']
            if error_rate > self.performance_thresholds['max_error_rate']:
                recommendations.append(OptimizationRecommendation(
                    category='reliability',
                    priority='high',
                    title='Improve Error Handling',
                    description=f"Error rate of {error_rate:.2%} exceeds threshold",
                    expected_improvement='95%+ success rate',
                    implementation_effort='medium',
                    metrics_affected=['error_count', 'success_rate']
                ))
        
        return recommendations
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        if not self._snapshots:
            return {'status': 'no_data'}
        
        analysis = self.analyze_performance()
        recommendations = self.get_optimization_recommendations()
        
        return {
            'analysis': analysis,
            'recommendations': [r.__dict__ for r in recommendations],
            'snapshot_count': len(self._snapshots),
            'analysis_time': self._last_analysis_time.isoformat() if self._last_analysis_time else None
        }
    
    def clear_data(self) -> None:
        """Clear all collected data."""
        self._snapshots.clear()
        self._error_history.clear()
        self._performance_history.clear()
        self._cached_analysis = None
        self._last_analysis_time = None
        self.logger.info("Cleared all analytics data")







