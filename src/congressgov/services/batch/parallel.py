"""Distributes batch work across multiple workers with load balancing and progress monitoring."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable, Union
import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

from .base import BaseBatchProcessor, BatchConfig, BatchResult, BatchStatus

logger = logging.getLogger(__name__)


class ParallelProcessor(BaseBatchProcessor):
    """
    Parallel processor for multi-worker batch operations.
    
    This class distributes work across multiple workers (threads or processes)
    with load balancing, progress monitoring, and graceful shutdown.
    
    Example:
        processor = ParallelProcessor(
            max_workers=5,
            chunk_size=20,
            worker_type='thread'  # or 'process'
        )
        
        # Process items in parallel
        results = await processor.process_items(
            items,
            operation=process_item
        )
    """
    
    def __init__(
        self,
        config: Optional[BatchConfig] = None,
        max_workers: Optional[int] = None,
        chunk_size: Optional[int] = None,
        worker_type: str = 'thread'
    ):
        """
        Initialize the parallel processor.
        
        Args:
            config: Batch configuration (uses default if None)
            max_workers: Maximum number of workers (default: CPU count)
            chunk_size: Size of chunks to distribute to workers
            worker_type: Type of workers ('thread' or 'process')
        """
        super().__init__(config)
        
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.chunk_size = chunk_size or self.config.chunk_size
        self.worker_type = worker_type.lower()
        
        if self.worker_type not in ['thread', 'process']:
            raise ValueError("worker_type must be 'thread' or 'process'")
        
        self._executor: Optional[Union[ThreadPoolExecutor, ProcessPoolExecutor]] = None
        self._worker_tasks: List[asyncio.Task] = []
        self._result_queue: asyncio.Queue = asyncio.Queue()
        self._error_queue: asyncio.Queue = asyncio.Queue()
    
    async def process_batch(self, items: List[Any], operation: Callable[[Any], Any]) -> BatchResult:
        """
        Process a batch of items using parallel workers.
        
        Args:
            items: List of items to process
            operation: Function to apply to each item
            
        Returns:
            BatchResult with processing details
        """
        if not items:
            return BatchResult(total_items=0)
        
        result = self._create_result(len(items))
        
        try:
            # Create executor
            if self.worker_type == 'thread':
                self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
            else:
                self._executor = ProcessPoolExecutor(max_workers=self.max_workers)
            
            # Split items into chunks
            chunks = self._split_into_chunks(items, self.chunk_size)
            
            # Create worker tasks
            worker_tasks = []
            for i, chunk in enumerate(chunks):
                if self.is_cancelled():
                    break
                
                task = asyncio.create_task(
                    self._process_chunk(i, chunk, operation, result)
                )
                worker_tasks.append(task)
            
            # Wait for all workers to complete
            if worker_tasks:
                await asyncio.gather(*worker_tasks, return_exceptions=True)
            
            # Complete the result
            if not self.is_cancelled():
                result.complete()
                self._log_performance(result)
            
        except Exception as e:
            logger.error(f"Parallel processing failed: {e}")
            result.fail()
            raise
        finally:
            # Clean up executor
            if self._executor:
                self._executor.shutdown(wait=True)
                self._executor = None
        
        return result
    
    async def process_items(
        self,
        items: List[Any],
        operation: Callable[[Any], Any],
        **kwargs
    ) -> List[Any]:
        """
        Process items using parallel workers.
        
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
            raise RuntimeError(f"Parallel processing failed: {len(result.errors)} errors")
        
        return result.results
    
    async def _process_chunk(
        self,
        chunk_id: int,
        chunk: List[Any],
        operation: Callable[[Any], Any],
        result: BatchResult
    ) -> None:
        """
        Process a chunk of items in a worker.
        
        Args:
            chunk_id: Unique identifier for this chunk
            chunk: List of items in this chunk
            operation: Operation to apply to each item
            result: Shared result object
        """
        if self.is_cancelled() or not chunk:
            return
        
        logger.debug(f"Worker {chunk_id} processing {len(chunk)} items")
        
        # Process each item in the chunk
        for item in chunk:
            if self.is_cancelled():
                break
            
            try:
                # Run operation in executor
                if asyncio.iscoroutinefunction(operation):
                    # Async operation - run directly
                    operation_result = await operation(item)
                else:
                    # Sync operation - run in executor
                    loop = asyncio.get_event_loop()
                    operation_result = await loop.run_in_executor(
                        self._executor, operation, item
                    )
                
                # Add success to result
                result.add_success(item, operation_result)
                
            except Exception as e:
                logger.error(f"Worker {chunk_id} failed to process item {item}: {e}")
                result.add_failure(item, e)
                
                # Check if we should continue on error
                if not self.config.continue_on_error:
                    self.cancel()
                    break
        
        logger.debug(f"Worker {chunk_id} completed processing {len(chunk)} items")
    
    def _split_into_chunks(self, items: List[Any], chunk_size: int) -> List[List[Any]]:
        """
        Split items into chunks for parallel processing.
        
        Args:
            items: List of items to split
            chunk_size: Maximum size of each chunk
            
        Returns:
            List of chunks
        """
        chunks = []
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    def _get_optimal_chunk_size(self, total_items: int) -> int:
        """
        Calculate optimal chunk size based on total items and workers.
        
        Args:
            total_items: Total number of items to process
            
        Returns:
            Optimal chunk size
        """
        if total_items <= self.max_workers:
            return 1
        
        # Aim for roughly equal distribution
        base_chunk_size = total_items // self.max_workers
        return max(1, base_chunk_size)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type:
            self.cancel()
        
        # Cancel any remaining tasks
        for task in self._worker_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        
        # Clean up executor
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None


class LoadBalancedProcessor(ParallelProcessor):
    """
    Load-balanced parallel processor with dynamic work distribution.
    
    This processor dynamically distributes work based on worker performance
    and current load, providing better load balancing than fixed chunk sizes.
    """
    
    def __init__(
        self,
        config: Optional[BatchConfig] = None,
        max_workers: Optional[int] = None,
        initial_chunk_size: int = 10,
        worker_type: str = 'thread'
    ):
        """
        Initialize the load-balanced processor.
        
        Args:
            config: Batch configuration (uses default if None)
            max_workers: Maximum number of workers
            initial_chunk_size: Initial chunk size for work distribution
            worker_type: Type of workers ('thread' or 'process')
        """
        super().__init__(config, max_workers, initial_chunk_size, worker_type)
        self.initial_chunk_size = initial_chunk_size
        self.work_queue: asyncio.Queue = asyncio.Queue()
        self.worker_stats: Dict[int, Dict[str, Any]] = {}
    
    async def process_batch(self, items: List[Any], operation: Callable[[Any], Any]) -> BatchResult:
        """
        Process items with load balancing.
        
        Args:
            items: List of items to process
            operation: Function to apply to each item
            
        Returns:
            BatchResult with processing details
        """
        if not items:
            return BatchResult(total_items=0)
        
        result = self._create_result(len(items))
        
        try:
            # Create executor
            if self.worker_type == 'thread':
                self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
            else:
                self._executor = ProcessPoolExecutor(max_workers=self.max_workers)
            
            # Add all items to work queue
            for item in items:
                await self.work_queue.put(item)
            
            # Create worker tasks
            worker_tasks = []
            for worker_id in range(self.max_workers):
                task = asyncio.create_task(
                    self._worker_loop(worker_id, operation, result)
                )
                worker_tasks.append(task)
            
            # Wait for all work to be completed
            await self.work_queue.join()
            
            # Cancel worker tasks
            for task in worker_tasks:
                task.cancel()
            
            # Wait for workers to finish
            await asyncio.gather(*worker_tasks, return_exceptions=True)
            
            # Complete the result
            if not self.is_cancelled():
                result.complete()
                self._log_performance(result)
            
        except Exception as e:
            logger.error(f"Load-balanced processing failed: {e}")
            result.fail()
            raise
        finally:
            # Clean up executor
            if self._executor:
                self._executor.shutdown(wait=True)
                self._executor = None
        
        return result
    
    async def _worker_loop(
        self,
        worker_id: int,
        operation: Callable[[Any], Any],
        result: BatchResult
    ) -> None:
        """
        Worker loop that processes items from the work queue.
        
        Args:
            worker_id: Unique identifier for this worker
            operation: Operation to apply to each item
            result: Shared result object
        """
        # Initialize worker stats
        self.worker_stats[worker_id] = {
            'items_processed': 0,
            'total_time': 0.0,
            'last_activity': time.time()
        }
        
        while not self.is_cancelled():
            try:
                # Get next item with timeout
                item = await asyncio.wait_for(self.work_queue.get(), timeout=1.0)
                
                start_time = time.time()
                
                try:
                    # Process item
                    if asyncio.iscoroutinefunction(operation):
                        operation_result = await operation(item)
                    else:
                        loop = asyncio.get_event_loop()
                        operation_result = await loop.run_in_executor(
                            self._executor, operation, item
                        )
                    
                    # Add success to result
                    result.add_success(item, operation_result)
                    
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed to process item {item}: {e}")
                    result.add_failure(item, e)
                    
                    if not self.config.continue_on_error:
                        self.cancel()
                        break
                
                # Update worker stats
                processing_time = time.time() - start_time
                self.worker_stats[worker_id]['items_processed'] += 1
                self.worker_stats[worker_id]['total_time'] += processing_time
                self.worker_stats[worker_id]['last_activity'] = time.time()
                
                # Mark task as done
                self.work_queue.task_done()
                
            except asyncio.TimeoutError:
                # No work available, check if we should continue
                if self.work_queue.empty():
                    break
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                break
        
        logger.debug(f"Worker {worker_id} completed")
    
    def get_worker_stats(self) -> Dict[int, Dict[str, Any]]:
        """Get statistics for all workers."""
        return self.worker_stats.copy()
    
    def get_load_balance_ratio(self) -> float:
        """Get the load balance ratio (0.0 = perfect balance, 1.0 = worst balance)."""
        if not self.worker_stats:
            return 0.0
        
        items_processed = [stats['items_processed'] for stats in self.worker_stats.values()]
        if not items_processed:
            return 0.0
        
        max_items = max(items_processed)
        min_items = min(items_processed)
        
        if max_items == 0:
            return 0.0
        
        return (max_items - min_items) / max_items







