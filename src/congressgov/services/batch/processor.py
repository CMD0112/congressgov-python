"""Async bulk operations with configurable concurrency, retry logic, and progress tracking."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
import asyncio
import logging

from .base import BaseBatchProcessor, BatchConfig, BatchResult, BatchStatus

logger = logging.getLogger(__name__)


class BatchProcessor(BaseBatchProcessor):
    """Async bulk operations with configurable concurrency, retry logic, and progress tracking.

    Example:
        processor = BatchProcessor(
            max_concurrent=10,
            batch_size=50,
            retry_failed=True
        )
        
        # Bulk fetch with progress tracking
        bills = await processor.bulk_fetch(
            bill_service.get,
            params_list=[
                {"congress": 118, "bill_type": "hr", "bill_number": i}
                for i in range(1, 101)
            ]
        )
    """
    
    def __init__(self, config: Optional[BatchConfig] = None):
        """
        Initialize the batch processor.
        
        Args:
            config: Batch configuration (uses default if None)
        """
        super().__init__(config)
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._tasks: List[asyncio.Task] = []
    
    async def process_batch(self, items: List[Any], operation: Callable[[Any], Any]) -> BatchResult:
        """
        Process a batch of items with the specified operation.
        
        Args:
            items: List of items to process
            operation: Function to apply to each item
            
        Returns:
            BatchResult with processing details
        """
        if not items:
            return BatchResult(total_items=0)
        
        result = self._create_result(len(items))
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
        try:
            # Create operation wrapper with timeout and error handling
            operation_wrapper = self._create_operation_wrapper(
                operation,
                self.config.operation_timeout,
                "batch_operation"
            )
            
            # Process items with concurrency control
            tasks = []
            for item in items:
                if self.is_cancelled():
                    result.cancel()
                    break
                
                task = asyncio.create_task(
                    self._process_item(item, operation_wrapper, result)
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Complete the result
            if not self.is_cancelled():
                result.complete()
                self._log_performance(result)
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            result.fail()
            raise
        finally:
            # Clean up
            self._semaphore = None
            self._tasks.clear()
        
        return result
    
    async def bulk_fetch(
        self,
        fetch_func: Callable[..., Any],
        params_list: List[Dict[str, Any]],
        **kwargs
    ) -> List[Any]:
        """
        Bulk fetch items using the provided fetch function.
        
        Args:
            fetch_func: Function to fetch individual items
            params_list: List of parameter dictionaries for each fetch
            **kwargs: Additional keyword arguments for fetch function
            
        Returns:
            List of successfully fetched items
        """
        if not params_list:
            return []
        
        # Create operation that calls fetch_func with parameters
        async def fetch_operation(params: Dict[str, Any]) -> Any:
            # Merge params with kwargs
            call_params = {**params, **kwargs}
            return await fetch_func(**call_params)
        
        # Process all items
        result = await self.process_batch(params_list, fetch_operation)
        
        if result.status == BatchStatus.FAILED:
            raise RuntimeError(f"Bulk fetch failed: {len(result.errors)} errors")
        
        return result.results
    
    async def bulk_process(
        self,
        items: List[Any],
        operation: Callable[[Any], Any],
        **kwargs
    ) -> List[Any]:
        """
        Bulk process items using the provided operation.
        
        Args:
            items: List of items to process
            operation: Function to process each item
            **kwargs: Additional keyword arguments for operation
            
        Returns:
            List of successfully processed items
        """
        if not items:
            return []
        
        # Create operation wrapper with kwargs
        def process_operation(item: Any) -> Any:
            if asyncio.iscoroutinefunction(operation):
                return operation(item, **kwargs)
            else:
                return operation(item, **kwargs)
        
        # Process all items
        result = await self.process_batch(items, process_operation)
        
        if result.status == BatchStatus.FAILED:
            raise RuntimeError(f"Bulk process failed: {len(result.errors)} errors")
        
        return result.results
    
    async def process_with_concurrency(
        self,
        items: List[Any],
        operation: Callable[[Any], Any],
        max_concurrent: Optional[int] = None,
        **kwargs
    ) -> List[Any]:
        """
        Process items with custom concurrency limit.
        
        Args:
            items: List of items to process
            operation: Function to process each item
            max_concurrent: Maximum concurrent operations (overrides config)
            **kwargs: Additional keyword arguments for operation
            
        Returns:
            List of successfully processed items
        """
        # Temporarily override concurrency
        original_concurrent = self.config.max_concurrent
        if max_concurrent is not None:
            self.config.max_concurrent = max_concurrent
        
        try:
            return await self.bulk_process(items, operation, **kwargs)
        finally:
            # Restore original concurrency
            self.config.max_concurrent = original_concurrent
    
    async def _process_item(
        self,
        item: Any,
        operation: Callable[[Any], Any],
        result: BatchResult
    ) -> None:
        """
        Process a single item with retry logic and error handling.
        
        Args:
            item: Item to process
            operation: Operation to apply to the item
            result: Batch result to update
        """
        if self.is_cancelled():
            return
        
        # Acquire semaphore for concurrency control
        async with self._semaphore:
            if self.is_cancelled():
                return
            
            # Retry logic
            last_error = None
            for attempt in range(self.config.max_retries + 1):
                try:
                    # Run operation with timeout
                    operation_result = await self._run_with_timeout(
                        operation(item),
                        self.config.operation_timeout,
                        f"operation for item {item}"
                    )
                    
                    # Success
                    result.add_success(item, operation_result)
                    return
                    
                except Exception as e:
                    last_error = e
                    
                    # Check if we should retry
                    if attempt < self.config.max_retries and self.config.should_retry(attempt + 1):
                        result.add_retry(item)
                        
                        # Calculate retry delay
                        delay = self.config.get_retry_delay(attempt + 1)
                        
                        logger.warning(
                            f"Operation failed for item {item} (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        
                        await asyncio.sleep(delay)
                    else:
                        # Final failure
                        logger.error(f"Operation failed for item {item} after {attempt + 1} attempts: {e}")
                        break
            
            # Add failure to result
            if last_error:
                result.add_failure(item, last_error)
                
                # Check if we should continue on error
                if not self.config.continue_on_error:
                    self.cancel()
                    raise last_error
    
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
    
    def _create_operation_wrapper(
        self,
        operation: Callable[[Any], Any],
        timeout: Optional[float] = None,
        operation_name: str = "operation"
    ) -> Callable[[Any], Any]:
        """Create a wrapper for an operation with timeout and error handling."""
        async def wrapper(item: Any) -> Any:
            try:
                if asyncio.iscoroutinefunction(operation):
                    result = await self._run_with_timeout(
                        operation(item), timeout, operation_name
                    )
                else:
                    # Run sync function in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, operation, item)
                
                return result
            except Exception as e:
                logger.error(f"Operation failed for item {item}: {e}")
                raise
        
        return wrapper
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type:
            self.cancel()
        
        # Cancel any remaining tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)







