"""
Resilient batch processor with comprehensive error handling.

This module provides the ResilientBatchProcessor class for handling batch
operations with robust error recovery, retry logic, and failure isolation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
import asyncio
import logging
import time
from datetime import datetime

from .base import BaseBatchProcessor, BatchConfig, BatchResult, BatchStatus, RetryStrategy
from .checkpoint import CheckpointManager

logger = logging.getLogger(__name__)


class ResilientBatchProcessor(BaseBatchProcessor):
    """
    Resilient batch processor with comprehensive error handling.
    
    This class provides robust batch processing with retry logic, error isolation,
    and comprehensive error recovery mechanisms.
    
    Example:
        processor = ResilientBatchProcessor(
            max_retries=3,
            retry_delay=2.0,
            continue_on_error=True,
            error_callback=log_error
        )
        
        # Process with error recovery
        results = await processor.process_batch(
            items,
            operation=process_item
        )
    """
    
    def __init__(
        self,
        config: Optional[BatchConfig] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_strategy: Optional[RetryStrategy] = None,
        continue_on_error: Optional[bool] = None,
        error_callback: Optional[Callable[[Exception, Any], None]] = None,
        success_callback: Optional[Callable[[Any], None]] = None,
        checkpoint_manager: Optional[CheckpointManager] = None
    ):
        """
        Initialize the resilient batch processor.
        
        Args:
            config: Batch configuration (uses default if None)
            max_retries: Maximum number of retries for failed items
            retry_delay: Base delay between retries
            retry_strategy: Strategy for calculating retry delays
            continue_on_error: Whether to continue processing on errors
            error_callback: Callback for handling errors
            success_callback: Callback for handling successes
            checkpoint_manager: Checkpoint manager for progress persistence
        """
        super().__init__(config)
        
        # Override config values if provided
        if max_retries is not None:
            self.config.max_retries = max_retries
        if retry_delay is not None:
            self.config.retry_delay = retry_delay
        if retry_strategy is not None:
            self.config.retry_strategy = retry_strategy
        if continue_on_error is not None:
            self.config.continue_on_error = continue_on_error
        if error_callback is not None:
            self.config.error_callback = error_callback
        if success_callback is not None:
            self.config.success_callback = success_callback
        
        self.checkpoint_manager = checkpoint_manager
        self._failed_items: List[Any] = []
        self._retry_queue: List[Dict[str, Any]] = []
        self._error_counts: Dict[str, int] = {}
        self._start_time: Optional[datetime] = None
    
    async def process_batch(self, items: List[Any], operation: Callable[[Any], Any]) -> BatchResult:
        """
        Process a batch of items with resilient error handling.
        
        Args:
            items: List of items to process
            operation: Function to apply to each item
            
        Returns:
            BatchResult with processing details
        """
        if not items:
            return BatchResult(total_items=0)
        
        result = self._create_result(len(items))
        self._start_time = datetime.now()
        
        try:
            # Process items with error handling
            await self._process_items_resilient(items, operation, result)
            
            # Retry failed items if configured
            if self.config.max_retries > 0 and self._retry_queue:
                await self._retry_failed_items(operation, result)
            
            # Complete the result
            if not self.is_cancelled():
                result.complete()
                self._log_performance(result)
            
        except Exception as e:
            logger.error(f"Resilient batch processing failed: {e}")
            result.fail()
            raise
        finally:
            # Save checkpoint if configured
            if self.checkpoint_manager:
                await self.checkpoint_manager.save_batch_result(result)
        
        return result
    
    async def _process_items_resilient(
        self,
        items: List[Any],
        operation: Callable[[Any], Any],
        result: BatchResult
    ) -> None:
        """
        Process items with resilient error handling.
        
        Args:
            items: List of items to process
            operation: Function to apply to each item
            result: Result object to update
        """
        for item in items:
            if self.is_cancelled():
                break
            
            try:
                # Process item
                operation_result = await self._process_item_with_retry(item, operation)
                
                # Add success to result
                result.add_success(item, operation_result)
                
            except Exception as e:
                logger.error(f"Failed to process item {item}: {e}")
                
                # Add to retry queue if retries are enabled
                if self.config.max_retries > 0:
                    self._retry_queue.append({
                        'item': item,
                        'error': e,
                        'attempt': 0,
                        'last_attempt_time': time.time()
                    })
                
                # Add failure to result
                result.add_failure(item, e)
                
                # Check if we should continue on error
                if not self.config.continue_on_error:
                    self.cancel()
                    break
    
    async def _process_item_with_retry(
        self,
        item: Any,
        operation: Callable[[Any], Any]
    ) -> Any:
        """
        Process a single item with retry logic.
        
        Args:
            item: Item to process
            operation: Operation to apply to the item
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # Run operation with timeout
                if asyncio.iscoroutinefunction(operation):
                    result = await self._run_with_timeout(
                        operation(item),
                        self.config.operation_timeout,
                        f"operation for item {item}"
                    )
                else:
                    # Run sync function in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, operation, item)
                
                return result
                
            except Exception as e:
                last_error = e
                
                # Check if we should retry
                if attempt < self.config.max_retries and self.config.should_retry(attempt + 1):
                    # Calculate retry delay
                    delay = self.config.get_retry_delay(attempt + 1)
                    
                    logger.warning(
                        f"Operation failed for item {item} (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
                else:
                    # Final failure
                    logger.error(f"Operation failed for item {item} after {attempt + 1} attempts: {e}")
                    break
        
        # All retries failed
        raise last_error
    
    async def _retry_failed_items(
        self,
        operation: Callable[[Any], Any],
        result: BatchResult
    ) -> None:
        """
        Retry failed items from the retry queue.
        
        Args:
            operation: Operation to apply to failed items
            result: Result object to update
        """
        if not self._retry_queue:
            return
        
        logger.info(f"Retrying {len(self._retry_queue)} failed items")
        
        # Process retry queue
        retry_items = self._retry_queue.copy()
        self._retry_queue.clear()
        
        for retry_item in retry_items:
            if self.is_cancelled():
                break
            
            item = retry_item['item']
            attempt = retry_item['attempt'] + 1
            
            try:
                # Process item
                operation_result = await self._process_item_with_retry(item, operation)
                
                # Add success to result
                result.add_success(item, operation_result)
                
                # Remove from failed items
                if item in self._failed_items:
                    self._failed_items.remove(item)
                
            except Exception as e:
                logger.error(f"Retry failed for item {item} (attempt {attempt}): {e}")
                
                # Update retry item
                retry_item['attempt'] = attempt
                retry_item['last_attempt_time'] = time.time()
                
                # Add back to retry queue if we haven't exceeded max retries
                if attempt < self.config.max_retries:
                    self._retry_queue.append(retry_item)
                else:
                    # Final failure
                    result.add_failure(item, e)
                    self._failed_items.append(item)
    
    async def _run_with_timeout(
        self,
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
    
    def get_failed_items(self) -> List[Any]:
        """Get list of items that failed processing."""
        return self._failed_items.copy()
    
    def get_retry_queue_size(self) -> int:
        """Get the number of items in the retry queue."""
        return len(self._retry_queue)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered."""
        return {
            'total_errors': len(self._error_counts),
            'error_types': self._error_counts.copy(),
            'failed_items_count': len(self._failed_items),
            'retry_queue_size': len(self._retry_queue)
        }
    
    async def resume_from_checkpoint(self) -> Optional[BatchResult]:
        """
        Resume processing from the last checkpoint.
        
        Returns:
            BatchResult from checkpoint or None if no checkpoint found
        """
        if not self.checkpoint_manager:
            logger.warning("No checkpoint manager configured")
            return None
        
        try:
            result = await self.checkpoint_manager.load_batch_result()
            if result:
                logger.info(f"Resumed from checkpoint: {result.processed_items} items processed")
            return result
            
        except Exception as e:
            logger.error(f"Failed to resume from checkpoint: {e}")
            return None
    
    def clear_failed_items(self) -> None:
        """Clear the list of failed items."""
        self._failed_items.clear()
        self._retry_queue.clear()
        self._error_counts.clear()
        logger.debug("Cleared failed items and retry queue")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type:
            self.cancel()
        
        # Save final checkpoint
        if self.checkpoint_manager:
            try:
                # Create a final result summary
                final_result = BatchResult(total_items=0)
                final_result.processed_items = len(self._failed_items) + len(self._retry_queue)
                final_result.failed_items = len(self._failed_items)
                final_result.status = BatchStatus.COMPLETED
                
                await self.checkpoint_manager.save_batch_result(final_result)
            except Exception as e:
                logger.error(f"Failed to save final checkpoint: {e}")


class CircuitBreakerProcessor(ResilientBatchProcessor):
    """
    Batch processor with circuit breaker pattern for failure protection.
    
    This processor automatically opens a circuit when too many failures occur,
    preventing cascading failures and allowing the system to recover.
    """
    
    def __init__(
        self,
        config: Optional[BatchConfig] = None,
        circuit_breaker_threshold: int = 10,
        circuit_breaker_timeout: float = 60.0,
        **kwargs
    ):
        """
        Initialize the circuit breaker processor.
        
        Args:
            config: Batch configuration (uses default if None)
            circuit_breaker_threshold: Number of failures before opening circuit
            circuit_breaker_timeout: Time to wait before trying half-open state
            **kwargs: Additional arguments for base class
        """
        super().__init__(config, **kwargs)
        
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        
        self._failure_count = 0
        self._last_failure_time = None
        self._circuit_state = 'closed'  # 'closed', 'open', 'half-open'
        self._circuit_open_time = None
    
    async def _process_item_with_retry(
        self,
        item: Any,
        operation: Callable[[Any], Any]
    ) -> Any:
        """
        Process item with circuit breaker protection.
        
        Args:
            item: Item to process
            operation: Operation to apply to the item
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If circuit is open or operation fails
        """
        # Check circuit state
        if self._circuit_state == 'open':
            if self._should_attempt_reset():
                self._circuit_state = 'half-open'
                logger.info("Circuit breaker moved to half-open state")
            else:
                raise RuntimeError("Circuit breaker is open - too many failures")
        
        try:
            # Process item
            result = await super()._process_item_with_retry(item, operation)
            
            # Reset failure count on success
            if self._circuit_state == 'half-open':
                self._circuit_state = 'closed'
                self._failure_count = 0
                logger.info("Circuit breaker closed - service recovered")
            
            return result
            
        except Exception as e:
            # Increment failure count
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            # Check if circuit should open
            if self._failure_count >= self.circuit_breaker_threshold:
                self._circuit_state = 'open'
                self._circuit_open_time = time.time()
                logger.warning(f"Circuit breaker opened after {self._failure_count} failures")
            
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if self._circuit_state != 'open' or not self._circuit_open_time:
            return False
        
        time_since_open = time.time() - self._circuit_open_time
        return time_since_open >= self.circuit_breaker_timeout
    
    def get_circuit_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            'state': self._circuit_state,
            'failure_count': self._failure_count,
            'last_failure_time': self._last_failure_time,
            'circuit_open_time': self._circuit_open_time,
            'threshold': self.circuit_breaker_threshold,
            'timeout': self.circuit_breaker_timeout
        }







