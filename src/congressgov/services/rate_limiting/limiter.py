"""
Rate limiter implementation with adaptive strategies.

This module provides sophisticated rate limiting with backoff strategies,
burst handling, and adaptive rate adjustment.
"""

from __future__ import annotations

from typing import Any, Optional, Dict
import time
import asyncio
import logging
import threading
from dataclasses import dataclass
from collections import deque

from .config import RateLimitConfig
from .backoff import ExponentialBackoff

logger = logging.getLogger(__name__)


@dataclass
class RateLimitState:
    """Current state of rate limiting."""
    
    requests_made: int = 0
    window_start: float = 0.0
    burst_tokens: int = 0
    last_request_time: float = 0.0
    consecutive_errors: int = 0
    current_delay: float = 0.0


class RateLimiter:
    """
    Intelligent rate limiter with adaptive strategies.
    
    Features:
    - Token bucket algorithm for burst handling
    - Exponential backoff on rate limit errors
    - Adaptive rate adjustment based on success/failure
    - Per-endpoint rate limiting
    - Async and sync support
    
    Example:
        limiter = RateLimiter(
            requests_per_second=10,
            burst_size=50,
            backoff_factor=2.0
        )
        
        # Sync usage
        limiter.acquire()
        make_api_call()
        
        # Async usage
        await limiter.acquire_async()
        await make_api_call()
    """
    
    def __init__(
        self,
        requests_per_second: float = 10.0,
        burst_size: int = 50,
        backoff_factor: float = 2.0,
        max_retries: int = 3,
        config: Optional[RateLimitConfig] = None,
        **kwargs
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum requests per second
            burst_size: Maximum burst size
            backoff_factor: Backoff multiplier for retries
            max_retries: Maximum number of retries
            config: Rate limit configuration
            **kwargs: Additional configuration
        """
        self.config = config or RateLimitConfig(
            requests_per_second=requests_per_second,
            burst_size=burst_size,
            backoff_factor=backoff_factor,
            max_retries=max_retries,
            **kwargs
        )
        
        # Rate limiting state
        self.state = RateLimitState()
        self.lock = threading.RLock()
        
        # Backoff strategy
        self.backoff = ExponentialBackoff(
            initial_delay=self.config.initial_delay,
            max_delay=self.config.max_delay,
            backoff_factor=self.config.backoff_factor
        )
        
        # Per-endpoint tracking
        self.endpoint_states: Dict[str, RateLimitState] = {}
        
        # Monitoring
        self.total_requests = 0
        self.total_delays = 0
        self.total_errors = 0
        
        logger.info(f"Rate limiter initialized: {requests_per_second} req/s, burst={burst_size}")
    
    def acquire(self, endpoint: str = "default") -> bool:
        """
        Acquire permission to make a request (sync).
        
        Args:
            endpoint: Endpoint identifier for per-endpoint limiting
            
        Returns:
            True if request is allowed, False if rate limited
        """
        with self.lock:
            return self._acquire_internal(endpoint)
    
    async def acquire_async(self, endpoint: str = "default") -> bool:
        """
        Acquire permission to make a request (async).
        
        Args:
            endpoint: Endpoint identifier for per-endpoint limiting
            
        Returns:
            True if request is allowed, False if rate limited
        """
        # Use asyncio.Lock for async safety
        async with asyncio.Lock():
            return self._acquire_internal(endpoint)
    
    def _acquire_internal(self, endpoint: str) -> bool:
        """
        Internal acquire logic.
        
        Args:
            endpoint: Endpoint identifier
            
        Returns:
            True if request is allowed
        """
        current_time = time.time()
        
        # Get or create endpoint state
        if endpoint not in self.endpoint_states:
            self.endpoint_states[endpoint] = RateLimitState()
        
        state = self.endpoint_states[endpoint]
        
        # Check if we need to reset the window
        if current_time - state.window_start >= 1.0:  # 1 second window
            state.requests_made = 0
            state.window_start = current_time
            state.burst_tokens = min(
                state.burst_tokens + self.config.burst_size,
                self.config.burst_size
            )
        
        # Check rate limit
        if state.requests_made >= self.config.requests_per_second:
            # Rate limited - check burst tokens
            if state.burst_tokens <= 0:
                logger.debug(f"Rate limited for endpoint: {endpoint}")
                return False
            
            # Use burst token
            state.burst_tokens -= 1
        
        # Check minimum delay between requests
        if state.last_request_time > 0:
            time_since_last = current_time - state.last_request_time
            min_interval = 1.0 / self.config.requests_per_second
            
            if time_since_last < min_interval:
                delay = min_interval - time_since_last
                time.sleep(delay)
                current_time = time.time()
        
        # Allow request
        state.requests_made += 1
        state.last_request_time = current_time
        self.total_requests += 1
        
        return True
    
    def record_success(self, endpoint: str = "default"):
        """
        Record a successful request.
        
        Args:
            endpoint: Endpoint identifier
        """
        with self.lock:
            if endpoint in self.endpoint_states:
                state = self.endpoint_states[endpoint]
                state.consecutive_errors = 0
                state.current_delay = 0.0
                
                # Gradually reduce delay on success
                if state.current_delay > 0:
                    state.current_delay *= 0.9
    
    def record_error(self, endpoint: str = "default", error_code: Optional[int] = None):
        """
        Record a request error.
        
        Args:
            endpoint: Endpoint identifier
            error_code: HTTP error code (429 for rate limit)
        """
        with self.lock:
            if endpoint not in self.endpoint_states:
                self.endpoint_states[endpoint] = RateLimitState()
            
            state = self.endpoint_states[endpoint]
            state.consecutive_errors += 1
            self.total_errors += 1
            
            # Apply backoff for rate limit errors
            if error_code == 429 or error_code in self.config.retry_on_status:
                delay = self.backoff.get_delay(state.consecutive_errors)
                state.current_delay = delay
                logger.warning(f"Rate limit error for {endpoint}, applying {delay:.2f}s delay")
    
    def wait_for_availability(self, endpoint: str = "default") -> float:
        """
        Wait for rate limit to allow next request.
        
        Args:
            endpoint: Endpoint identifier
            
        Returns:
            Time waited in seconds
        """
        start_time = time.time()
        
        while not self.acquire(endpoint):
            time.sleep(0.1)  # Small delay before retry
        
        return time.time() - start_time
    
    async def wait_for_availability_async(self, endpoint: str = "default") -> float:
        """
        Wait for rate limit to allow next request (async).
        
        Args:
            endpoint: Endpoint identifier
            
        Returns:
            Time waited in seconds
        """
        start_time = time.time()
        
        while not await self.acquire_async(endpoint):
            await asyncio.sleep(0.1)  # Small delay before retry
        
        return time.time() - start_time
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get rate limiting statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            stats = {
                'total_requests': self.total_requests,
                'total_errors': self.total_errors,
                'error_rate': self.total_errors / max(self.total_requests, 1),
                'endpoints': {}
            }
            
            for endpoint, state in self.endpoint_states.items():
                stats['endpoints'][endpoint] = {
                    'requests_made': state.requests_made,
                    'burst_tokens': state.burst_tokens,
                    'consecutive_errors': state.consecutive_errors,
                    'current_delay': state.current_delay,
                }
            
            return stats
    
    def reset(self, endpoint: Optional[str] = None):
        """
        Reset rate limiting state.
        
        Args:
            endpoint: Specific endpoint to reset (None for all)
        """
        with self.lock:
            if endpoint:
                if endpoint in self.endpoint_states:
                    del self.endpoint_states[endpoint]
            else:
                self.endpoint_states.clear()
                self.total_requests = 0
                self.total_errors = 0
                self.backoff.reset()
    
    def adjust_rate(self, new_rate: float):
        """
        Dynamically adjust the rate limit.
        
        Args:
            new_rate: New requests per second
        """
        with self.lock:
            self.config.requests_per_second = new_rate
            logger.info(f"Rate limit adjusted to {new_rate} req/s")
    
    def is_available(self, endpoint: str = "default") -> bool:
        """
        Check if requests are currently allowed.
        
        Args:
            endpoint: Endpoint identifier
            
        Returns:
            True if requests are allowed
        """
        with self.lock:
            if endpoint not in self.endpoint_states:
                return True
            
            state = self.endpoint_states[endpoint]
            current_time = time.time()
            
            # Check if window needs reset
            if current_time - state.window_start >= 1.0:
                return True
            
            # Check if under rate limit
            return state.requests_made < self.config.requests_per_second or state.burst_tokens > 0


class AdaptiveRateLimiter(RateLimiter):
    """
    Rate limiter that adapts based on API response patterns.
    
    This limiter automatically adjusts rate limits based on:
    - Success/failure patterns
    - Response times
    - Error rates
    - API feedback
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adaptive parameters
        self.base_rate = self.config.requests_per_second
        self.min_rate = self.base_rate * 0.1  # Minimum 10% of base rate
        self.max_rate = self.base_rate * 2.0  # Maximum 200% of base rate
        self.adaptation_factor = 0.1  # How quickly to adapt
        
        # Performance tracking
        self.response_times: deque = deque(maxlen=100)
        self.success_rate = 1.0
        
    def record_response_time(self, response_time: float):
        """
        Record response time for adaptive adjustment.
        
        Args:
            response_time: Response time in seconds
        """
        self.response_times.append(response_time)
        self._adapt_rate()
    
    def _adapt_rate(self):
        """Adapt rate based on performance metrics."""
        if len(self.response_times) < 10:  # Need sufficient data
            return
        
        # Calculate average response time
        avg_response_time = sum(self.response_times) / len(self.response_times)
        
        # Calculate success rate
        total_requests = len(self.response_times)
        successful_requests = total_requests - self.total_errors
        self.success_rate = successful_requests / total_requests
        
        # Adjust rate based on performance
        if avg_response_time > 1.0:  # Slow responses
            # Reduce rate
            new_rate = self.config.requests_per_second * (1 - self.adaptation_factor)
        elif avg_response_time < 0.1 and self.success_rate > 0.95:  # Fast responses, high success
            # Increase rate
            new_rate = self.config.requests_per_second * (1 + self.adaptation_factor)
        else:
            return  # No change needed
        
        # Clamp to min/max bounds
        new_rate = max(self.min_rate, min(self.max_rate, new_rate))
        
        if abs(new_rate - self.config.requests_per_second) > 0.1:  # Significant change
            self.adjust_rate(new_rate)
            logger.info(f"Adapted rate to {new_rate:.1f} req/s (success_rate={self.success_rate:.2f}, avg_time={avg_response_time:.3f}s)")







