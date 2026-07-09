"""
Circuit breaker pattern implementation for batch operations.

This module provides the CircuitBreaker class for protecting against cascading
failures during batch processing operations.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
import asyncio
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, requests are blocked
    HALF_OPEN = "half_open"  # Testing if service has recovered


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.
    
    This class implements the circuit breaker pattern to prevent cascading
    failures by opening the circuit when too many failures occur.
    
    Example:
        breaker = CircuitBreaker(
            failure_threshold=10,
            timeout=60.0,
            expected_exception=ConnectionError
        )
        
        # Use with async operations
        result = await breaker.call(operation, *args, **kwargs)
    """
    
    def __init__(
        self,
        failure_threshold: int = 10,
        timeout: float = 60.0,
        expected_exception: type = Exception,
        name: Optional[str] = None
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time to wait before trying half-open state
            expected_exception: Exception type to count as failures
            name: Name for logging purposes
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.name = name or f"CircuitBreaker-{id(self)}"
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{self.name}")
        
        # Circuit state
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._circuit_open_time: Optional[datetime] = None
        
        # Statistics
        self._total_requests = 0
        self._total_failures = 0
        self._total_successes = 0
        self._circuit_open_count = 0
        self._last_reset_time: Optional[datetime] = None
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call a function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: If the function call fails
        """
        self._total_requests += 1
        
        # Check circuit state
        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._state = CircuitState.HALF_OPEN
                self.logger.info("Circuit breaker moved to half-open state")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is open - {self.failure_count} failures, "
                    f"last failure at {self._last_failure_time}"
                )
        
        try:
            # Call the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, func, *args, **kwargs)
            
            # Success - reset failure count if circuit was half-open
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._last_reset_time = datetime.now()
                self.logger.info("Circuit breaker closed - service recovered")
            
            self._total_successes += 1
            return result
            
        except self.expected_exception as e:
            # Expected failure - increment failure count
            self._handle_failure()
            self.logger.warning(f"Circuit breaker recorded failure: {e}")
            raise e
            
        except Exception as e:
            # Unexpected failure - don't count as circuit breaker failure
            self.logger.error(f"Unexpected error in circuit breaker: {e}")
            raise e
    
    def _handle_failure(self) -> None:
        """Handle a failure in the circuit breaker."""
        self._failure_count += 1
        self._total_failures += 1
        self._last_failure_time = datetime.now()
        
        # Check if circuit should open
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._circuit_open_time = datetime.now()
            self._circuit_open_count += 1
            self.logger.warning(
                f"Circuit breaker opened after {self._failure_count} failures "
                f"(threshold: {self.failure_threshold})"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if self._state != CircuitState.OPEN or not self._circuit_open_time:
            return False
        
        time_since_open = datetime.now() - self._circuit_open_time
        return time_since_open.total_seconds() >= self.timeout
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self._state == CircuitState.OPEN
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed."""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open."""
        return self._state == CircuitState.HALF_OPEN
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        success_rate = (
            self._total_successes / self._total_requests * 100.0
            if self._total_requests > 0 else 0.0
        )
        
        return {
            'name': self.name,
            'state': self._state.value,
            'failure_count': self._failure_count,
            'failure_threshold': self.failure_threshold,
            'timeout': self.timeout,
            'total_requests': self._total_requests,
            'total_failures': self._total_failures,
            'total_successes': self._total_successes,
            'success_rate': success_rate,
            'circuit_open_count': self._circuit_open_count,
            'last_failure_time': self._last_failure_time.isoformat() if self._last_failure_time else None,
            'circuit_open_time': self._circuit_open_time.isoformat() if self._circuit_open_time else None,
            'last_reset_time': self._last_reset_time.isoformat() if self._last_reset_time else None
        }
    
    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._circuit_open_time = None
        self._last_reset_time = datetime.now()
        self.logger.info("Circuit breaker manually reset")
    
    def force_open(self) -> None:
        """Force the circuit breaker to open."""
        self._state = CircuitState.OPEN
        self._circuit_open_time = datetime.now()
        self._circuit_open_count += 1
        self.logger.warning("Circuit breaker forced open")
    
    def force_close(self) -> None:
        """Force the circuit breaker to close."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._circuit_open_time = None
        self._last_reset_time = datetime.now()
        self.logger.info("Circuit breaker forced closed")


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers.
    
    This class manages multiple circuit breakers and provides a unified
    interface for monitoring and controlling them.
    """
    
    def __init__(self):
        """Initialize the circuit breaker manager."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(
        self,
        name: str,
        failure_threshold: int = 10,
        timeout: float = 60.0,
        expected_exception: type = Exception
    ) -> CircuitBreaker:
        """
        Get or create a circuit breaker.
        
        Args:
            name: Name of the circuit breaker
            failure_threshold: Number of failures before opening circuit
            timeout: Time to wait before trying half-open state
            expected_exception: Exception type to count as failures
            
        Returns:
            Circuit breaker instance
        """
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                timeout=timeout,
                expected_exception=expected_exception,
                name=name
            )
            self.logger.debug(f"Created circuit breaker: {name}")
        
        return self._breakers[name]
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        return {name: breaker.get_stats() for name, breaker in self._breakers.items()}
    
    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for breaker in self._breakers.values():
            breaker.reset()
        self.logger.info("Reset all circuit breakers")
    
    def force_close_all(self) -> None:
        """Force all circuit breakers to close."""
        for breaker in self._breakers.values():
            breaker.force_close()
        self.logger.info("Forced all circuit breakers to close")
    
    def get_open_breakers(self) -> List[str]:
        """Get list of open circuit breakers."""
        return [name for name, breaker in self._breakers.items() if breaker.is_open]
    
    def remove_breaker(self, name: str) -> bool:
        """
        Remove a circuit breaker.
        
        Args:
            name: Name of the circuit breaker to remove
            
        Returns:
            True if breaker was found and removed
        """
        if name in self._breakers:
            del self._breakers[name]
            self.logger.debug(f"Removed circuit breaker: {name}")
            return True
        return False







