"""Configuration for rate limiting: retry logic, backoff strategy, and monitoring settings."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    
    FIXED = "fixed"  # Fixed rate limit
    ADAPTIVE = "adaptive"  # Adaptive rate based on performance
    BURST = "burst"  # Allow bursts with token bucket


@dataclass
class RateLimitConfig:
    """Rate limiting settings: request caps, retry logic, backoff strategy, and monitoring."""
    
    # Basic rate limiting
    requests_per_second: float = 10.0
    burst_size: int = 50
    strategy: RateLimitStrategy = RateLimitStrategy.BURST
    
    # Retry configuration
    max_retries: int = 3
    retry_on_status: Tuple[int, ...] = (429, 503, 502, 504)
    retry_on_exceptions: Tuple[type, ...] = (Exception,)
    
    # Backoff configuration
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True
    
    # Adaptive configuration
    enable_adaptive: bool = True
    adaptation_factor: float = 0.1
    min_rate_factor: float = 0.1  # Minimum 10% of base rate
    max_rate_factor: float = 2.0  # Maximum 200% of base rate
    
    # Monitoring
    enable_monitoring: bool = True
    alert_threshold: float = 0.8  # Alert when 80% of rate limit used
    stats_window: int = 100  # Number of requests to track for stats
    
    # Per-endpoint configuration
    endpoint_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Advanced options
    enable_circuit_breaker: bool = False
    circuit_breaker_threshold: int = 10  # Failures before opening circuit
    circuit_breaker_timeout: float = 60.0  # Seconds before trying again
    
    def get_endpoint_config(self, endpoint: str) -> 'RateLimitConfig':
        """
        Get configuration for a specific endpoint.
        
        Args:
            endpoint: Endpoint identifier
            
        Returns:
            Rate limit configuration for the endpoint
        """
        if endpoint not in self.endpoint_configs:
            return self
        
        # Create a copy with endpoint-specific overrides
        config = RateLimitConfig(
            requests_per_second=self.requests_per_second,
            burst_size=self.burst_size,
            strategy=self.strategy,
            max_retries=self.max_retries,
            retry_on_status=self.retry_on_status,
            retry_on_exceptions=self.retry_on_exceptions,
            backoff_factor=self.backoff_factor,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            jitter=self.jitter,
            enable_adaptive=self.enable_adaptive,
            adaptation_factor=self.adaptation_factor,
            min_rate_factor=self.min_rate_factor,
            max_rate_factor=self.max_rate_factor,
            enable_monitoring=self.enable_monitoring,
            alert_threshold=self.alert_threshold,
            stats_window=self.stats_window,
            enable_circuit_breaker=self.enable_circuit_breaker,
            circuit_breaker_threshold=self.circuit_breaker_threshold,
            circuit_breaker_timeout=self.circuit_breaker_timeout,
        )
        
        # Apply endpoint-specific overrides
        endpoint_config = self.endpoint_configs[endpoint]
        for key, value in endpoint_config.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def set_endpoint_config(self, endpoint: str, **overrides):
        """
        Set configuration overrides for an endpoint.
        
        Args:
            endpoint: Endpoint identifier
            **overrides: Configuration overrides
        """
        self.endpoint_configs[endpoint] = overrides
    
    def get_effective_rate(self, endpoint: str = "default") -> float:
        """
        Get effective rate limit for an endpoint.
        
        Args:
            endpoint: Endpoint identifier
            
        Returns:
            Effective rate limit in requests per second
        """
        config = self.get_endpoint_config(endpoint)
        return config.requests_per_second
    
    def get_effective_burst_size(self, endpoint: str = "default") -> int:
        """
        Get effective burst size for an endpoint.
        
        Args:
            endpoint: Endpoint identifier
            
        Returns:
            Effective burst size
        """
        config = self.get_endpoint_config(endpoint)
        return config.burst_size
    
    def should_retry(self, status_code: Optional[int], exception: Optional[Exception], attempt: int) -> bool:
        """
        Determine if a request should be retried.
        
        Args:
            status_code: HTTP status code
            exception: Exception that occurred
            attempt: Current attempt number
            
        Returns:
            True if request should be retried
        """
        if attempt >= self.max_retries:
            return False
        
        # Check status code
        if status_code is not None and status_code in self.retry_on_status:
            return True
        
        # Check exception type
        if exception is not None and isinstance(exception, self.retry_on_exceptions):
            return True
        
        return False
    
    def get_retry_delay(self, attempt: int, status_code: Optional[int] = None) -> float:
        """
        Get delay for retry attempt.
        
        Args:
            attempt: Current attempt number
            status_code: HTTP status code
            
        Returns:
            Delay in seconds
        """
        if attempt <= 0:
            return 0.0
        
        # Calculate base delay
        delay = self.initial_delay * (self.backoff_factor ** (attempt - 1))
        
        # Apply maximum delay limit
        delay = min(delay, self.max_delay)
        
        # Add jitter if enabled
        if self.jitter:
            import random
            jitter_amount = delay * 0.25 * random.random()
            delay += jitter_amount
        
        # Special handling for rate limit errors
        if status_code == 429:
            # Add extra delay for rate limit errors
            delay *= 1.5
        
        return delay
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            'requests_per_second': self.requests_per_second,
            'burst_size': self.burst_size,
            'strategy': self.strategy.value,
            'max_retries': self.max_retries,
            'retry_on_status': self.retry_on_status,
            'backoff_factor': self.backoff_factor,
            'initial_delay': self.initial_delay,
            'max_delay': self.max_delay,
            'jitter': self.jitter,
            'enable_adaptive': self.enable_adaptive,
            'adaptation_factor': self.adaptation_factor,
            'min_rate_factor': self.min_rate_factor,
            'max_rate_factor': self.max_rate_factor,
            'enable_monitoring': self.enable_monitoring,
            'alert_threshold': self.alert_threshold,
            'stats_window': self.stats_window,
            'endpoint_configs': self.endpoint_configs,
            'enable_circuit_breaker': self.enable_circuit_breaker,
            'circuit_breaker_threshold': self.circuit_breaker_threshold,
            'circuit_breaker_timeout': self.circuit_breaker_timeout,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RateLimitConfig':
        """
        Create configuration from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Rate limit configuration
        """
        # Handle enum conversion
        if 'strategy' in data and isinstance(data['strategy'], str):
            data['strategy'] = RateLimitStrategy(data['strategy'])
        
        # Handle tuple conversion
        if 'retry_on_status' in data and isinstance(data['retry_on_status'], list):
            data['retry_on_status'] = tuple(data['retry_on_status'])
        
        return cls(**data)


# Predefined configurations for common use cases
def get_conservative_config() -> RateLimitConfig:
    """Get conservative rate limiting configuration."""
    return RateLimitConfig(
        requests_per_second=5.0,
        burst_size=20,
        max_retries=5,
        initial_delay=2.0,
        max_delay=120.0,
        enable_adaptive=True,
    )


def get_aggressive_config() -> RateLimitConfig:
    """Get aggressive rate limiting configuration."""
    return RateLimitConfig(
        requests_per_second=20.0,
        burst_size=100,
        max_retries=2,
        initial_delay=0.5,
        max_delay=30.0,
        enable_adaptive=True,
    )


def get_development_config() -> RateLimitConfig:
    """Get development rate limiting configuration."""
    return RateLimitConfig(
        requests_per_second=1.0,
        burst_size=5,
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        enable_monitoring=False,
    )


def get_production_config() -> RateLimitConfig:
    """Get production rate limiting configuration."""
    return RateLimitConfig(
        requests_per_second=10.0,
        burst_size=50,
        max_retries=3,
        initial_delay=1.0,
        max_delay=60.0,
        enable_adaptive=True,
        enable_monitoring=True,
        enable_circuit_breaker=True,
    )







