"""Backoff strategies for handling rate limits and retries."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod


class BackoffStrategy(ABC):
    """Abstract base class for backoff strategies."""
    
    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """
        Get delay for a specific attempt.
        
        Args:
            attempt: The attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        pass
    
    def reset(self):
        """Reset the backoff strategy."""
        pass


class ExponentialBackoff(BackoffStrategy):
    """
    Exponential backoff strategy.
    
    Delay increases exponentially with each attempt, with optional
    jitter to prevent thundering herd problems.
    """
    
    def __init__(
        self,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize exponential backoff.
        
        Args:
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Multiplier for each attempt
            jitter: Add random jitter to prevent thundering herd
        """
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """
        Get exponential delay for attempt.
        
        Args:
            attempt: The attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        if attempt <= 0:
            return 0.0
        
        # Calculate exponential delay
        delay = self.initial_delay * (self.backoff_factor ** (attempt - 1))
        
        # Apply maximum delay limit
        delay = min(delay, self.max_delay)
        
        # Add jitter if enabled
        if self.jitter:
            # Add up to 25% random jitter
            jitter_amount = delay * 0.25 * random.random()
            delay += jitter_amount
        
        return delay


class LinearBackoff(BackoffStrategy):
    """
    Linear backoff strategy.
    
    Delay increases linearly with each attempt.
    """
    
    def __init__(
        self,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        increment: float = 1.0
    ):
        """
        Initialize linear backoff.
        
        Args:
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            increment: Delay increment per attempt
        """
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.increment = increment
    
    def get_delay(self, attempt: int) -> float:
        """
        Get linear delay for attempt.
        
        Args:
            attempt: The attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        if attempt <= 0:
            return 0.0
        
        # Calculate linear delay
        delay = self.initial_delay + (self.increment * (attempt - 1))
        
        # Apply maximum delay limit
        return min(delay, self.max_delay)


class FixedBackoff(BackoffStrategy):
    """
    Fixed backoff strategy.
    
    Uses the same delay for all attempts.
    """
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize fixed backoff.
        
        Args:
            delay: Fixed delay in seconds
        """
        self.delay = delay
    
    def get_delay(self, attempt: int) -> float:
        """
        Get fixed delay for attempt.
        
        Args:
            attempt: The attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        return self.delay if attempt > 0 else 0.0


class FibonacciBackoff(BackoffStrategy):
    """
    Fibonacci backoff strategy.
    
    Delay follows the Fibonacci sequence.
    """
    
    def __init__(
        self,
        initial_delay: float = 1.0,
        max_delay: float = 60.0
    ):
        """
        Initialize Fibonacci backoff.
        
        Args:
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
        """
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self._fib_cache = {0: 0, 1: 1}
    
    def _fibonacci(self, n: int) -> int:
        """Calculate Fibonacci number with caching."""
        if n not in self._fib_cache:
            self._fib_cache[n] = self._fibonacci(n - 1) + self._fibonacci(n - 2)
        return self._fib_cache[n]
    
    def get_delay(self, attempt: int) -> float:
        """
        Get Fibonacci delay for attempt.
        
        Args:
            attempt: The attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        if attempt <= 0:
            return 0.0
        
        # Get Fibonacci number
        fib = self._fibonacci(attempt)
        
        # Calculate delay
        delay = self.initial_delay * fib
        
        # Apply maximum delay limit
        return min(delay, self.max_delay)


class AdaptiveBackoff(BackoffStrategy):
    """
    Adaptive backoff strategy.
    
    Adjusts backoff based on success/failure patterns.
    """
    
    def __init__(
        self,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        min_delay: float = 0.1,
        success_factor: float = 0.9,
        failure_factor: float = 1.5
    ):
        """
        Initialize adaptive backoff.
        
        Args:
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            min_delay: Minimum delay in seconds
            success_factor: Multiplier on success
            failure_factor: Multiplier on failure
        """
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.min_delay = min_delay
        self.success_factor = success_factor
        self.failure_factor = failure_factor
        self.current_delay = initial_delay
        self.consecutive_failures = 0
    
    def get_delay(self, attempt: int) -> float:
        """
        Get adaptive delay for attempt.
        
        Args:
            attempt: The attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        if attempt <= 0:
            return 0.0
        
        # Increase delay on consecutive failures
        if self.consecutive_failures > 0:
            self.current_delay *= self.failure_factor
        else:
            # Decrease delay on success
            self.current_delay *= self.success_factor
        
        # Clamp to bounds
        self.current_delay = max(
            self.min_delay,
            min(self.current_delay, self.max_delay)
        )
        
        return self.current_delay
    
    def record_success(self):
        """Record a successful attempt."""
        self.consecutive_failures = 0
    
    def record_failure(self):
        """Record a failed attempt."""
        self.consecutive_failures += 1
    
    def reset(self):
        """Reset the adaptive backoff."""
        self.current_delay = self.initial_delay
        self.consecutive_failures = 0


class CompositeBackoff(BackoffStrategy):
    """
    Composite backoff strategy.
    
    Combines multiple backoff strategies with different weights.
    """
    
    def __init__(self, strategies: list[tuple[BackoffStrategy, float]]):
        """
        Initialize composite backoff.
        
        Args:
            strategies: List of (strategy, weight) tuples
        """
        self.strategies = strategies
        self.total_weight = sum(weight for _, weight in strategies)
    
    def get_delay(self, attempt: int) -> float:
        """
        Get weighted average delay for attempt.
        
        Args:
            attempt: The attempt number (0-based)
            
        Returns:
            Weighted average delay in seconds
        """
        if attempt <= 0:
            return 0.0
        
        weighted_delay = 0.0
        for strategy, weight in self.strategies:
            delay = strategy.get_delay(attempt)
            weighted_delay += delay * weight
        
        return weighted_delay / self.total_weight
    
    def reset(self):
        """Reset all strategies."""
        for strategy, _ in self.strategies:
            strategy.reset()







