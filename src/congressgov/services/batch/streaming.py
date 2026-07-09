"""
Streaming processor for memory-efficient batch operations.

This module provides the StreamingProcessor class for processing large datasets
without loading everything into memory at once.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable, AsyncIterator
import asyncio
import logging
from datetime import datetime
import gc

from .base import BaseBatchProcessor, BatchConfig, BatchResult
from .memory import MemoryMonitor

logger = logging.getLogger(__name__)


class StreamingProcessor(BaseBatchProcessor):
    """
    Streaming processor for memory-efficient batch operations.
    
    This class processes large datasets by streaming data in batches,
    monitoring memory usage, and automatically adjusting batch sizes.
    
    Example:
        processor = StreamingProcessor(
            batch_size=100,
            max_memory_mb=1000,
            checkpoint_interval=1000
        )
        
        # Stream and process large dataset
        async for batch in processor.stream_items(data_source):
            await process_batch(batch)
    """
    
    def __init__(
        self,
        config: Optional[BatchConfig] = None,
        batch_size: Optional[int] = None,
        max_memory_mb: Optional[int] = None,
        checkpoint_interval: Optional[int] = None
    ):
        """
        Initialize the streaming processor.
        
        Args:
            config: Batch configuration (uses default if None)
            batch_size: Size of batches to process
            max_memory_mb: Maximum memory usage in MB
            checkpoint_interval: Interval for saving checkpoints
        """
        super().__init__(config)
        
        # Override config values if provided
        if batch_size is not None:
            self.config.batch_size = batch_size
        if max_memory_mb is not None:
            self.config.max_memory_mb = max_memory_mb
        if checkpoint_interval is not None:
            self.config.checkpoint_interval = checkpoint_interval
        
        self.memory_monitor = MemoryMonitor()
        self._current_batch: List[Any] = []
        self._processed_count = 0
        self._checkpoint_count = 0
    
    async def process_batch(self, items: List[Any], operation: Callable[[Any], Any]) -> BatchResult:
        """
        Process a batch of items using streaming.
        
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
            # Process items in streaming batches
            async for batch in self._stream_items(items):
                if self.is_cancelled():
                    break
                
                # Process batch
                await self._process_streaming_batch(batch, operation, result)
                
                # Update progress
                self._update_progress(result)
                
                # Check memory usage
                if self.config.max_memory_mb:
                    memory_usage = self.memory_monitor.get_memory_usage_mb()
                    if memory_usage > self.config.max_memory_mb:
                        logger.warning(f"Memory usage {memory_usage:.1f}MB exceeds limit {self.config.max_memory_mb}MB")
                        # Force garbage collection
                        gc.collect()
            
            # Complete the result
            if not self.is_cancelled():
                result.complete()
                self._log_performance(result)
            
        except Exception as e:
            logger.error(f"Streaming processing failed: {e}")
            result.fail()
            raise
        
        return result
    
    async def stream_items(
        self,
        source: AsyncIterator[Any],
        batch_size: Optional[int] = None
    ) -> AsyncIterator[List[Any]]:
        """
        Stream items from source in batches.
        
        Args:
            source: Async iterator of items
            batch_size: Size of batches (overrides config)
            
        Yields:
            List of items in each batch
        """
        batch_size = batch_size or self.config.batch_size
        current_batch = []
        
        async for item in source:
            if self.is_cancelled():
                break
            
            current_batch.append(item)
            
            # Yield batch when it reaches the desired size
            if len(current_batch) >= batch_size:
                yield current_batch
                current_batch = []
                
                # Check memory usage
                if self.config.max_memory_mb:
                    memory_usage = self.memory_monitor.get_memory_usage_mb()
                    if memory_usage > self.config.max_memory_mb:
                        logger.warning(f"Memory usage {memory_usage:.1f}MB exceeds limit")
                        # Force garbage collection
                        gc.collect()
        
        # Yield remaining items
        if current_batch and not self.is_cancelled():
            yield current_batch
    
    async def stream_with_memory_limit(
        self,
        source: AsyncIterator[Any],
        max_memory_mb: int
    ) -> AsyncIterator[List[Any]]:
        """
        Stream items with dynamic batch sizing based on memory usage.
        
        Args:
            source: Async iterator of items
            max_memory_mb: Maximum memory usage in MB
            
        Yields:
            List of items in each batch
        """
        current_batch = []
        batch_size = self.config.batch_size
        
        async for item in source:
            if self.is_cancelled():
                break
            
            current_batch.append(item)
            
            # Check if we should yield the batch
            should_yield = (
                len(current_batch) >= batch_size or
                self.memory_monitor.get_memory_usage_mb() > max_memory_mb
            )
            
            if should_yield:
                yield current_batch
                current_batch = []
                
                # Adjust batch size based on memory usage
                memory_usage = self.memory_monitor.get_memory_usage_mb()
                if memory_usage > max_memory_mb * 0.8:  # 80% of limit
                    batch_size = max(1, batch_size // 2)
                elif memory_usage < max_memory_mb * 0.5:  # 50% of limit
                    batch_size = min(batch_size * 2, self.config.batch_size * 4)
                
                # Force garbage collection if needed
                if memory_usage > max_memory_mb * 0.9:  # 90% of limit
                    gc.collect()
        
        # Yield remaining items
        if current_batch and not self.is_cancelled():
            yield current_batch
    
    async def _stream_items(self, items: List[Any]) -> AsyncIterator[List[Any]]:
        """
        Stream items in batches.
        
        Args:
            items: List of items to stream
            
        Yields:
            List of items in each batch
        """
        batch_size = self.config.batch_size
        
        for i in range(0, len(items), batch_size):
            if self.is_cancelled():
                break
            
            batch = items[i:i + batch_size]
            yield batch
    
    async def _process_streaming_batch(
        self,
        batch: List[Any],
        operation: Callable[[Any], Any],
        result: BatchResult
    ) -> None:
        """
        Process a streaming batch of items.
        
        Args:
            batch: Batch of items to process
            operation: Operation to apply to each item
            result: Result object to update
        """
        for item in batch:
            if self.is_cancelled():
                break
            
            try:
                # Process item
                if asyncio.iscoroutinefunction(operation):
                    operation_result = await operation(item)
                else:
                    loop = asyncio.get_event_loop()
                    operation_result = await loop.run_in_executor(None, operation, item)
                
                # Add success to result
                result.add_success(item, operation_result)
                
            except Exception as e:
                logger.error(f"Failed to process item {item}: {e}")
                result.add_failure(item, e)
                
                if not self.config.continue_on_error:
                    self.cancel()
                    break
        
        # Update processed count
        self._processed_count += len(batch)
        
        # Check if we should save checkpoint
        if self._should_checkpoint():
            await self._save_checkpoint(result)
    
    def _should_checkpoint(self) -> bool:
        """Check if a checkpoint should be saved."""
        return (
            self.config.checkpoint_interval > 0 and
            self._processed_count > 0 and
            self._processed_count % self.config.checkpoint_interval == 0
        )
    
    async def _save_checkpoint(self, result: BatchResult) -> None:
        """Save a checkpoint."""
        if self.config.checkpoint_file:
            checkpoint_data = {
                'processed_count': self._processed_count,
                'result': result.to_dict(),
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                import json
                with open(self.config.checkpoint_file, 'w') as f:
                    json.dump(checkpoint_data, f, indent=2)
                
                logger.debug(f"Checkpoint saved: {self._processed_count} items processed")
                
            except Exception as e:
                logger.error(f"Failed to save checkpoint: {e}")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        return self.memory_monitor.get_memory_stats()
    
    def get_processed_count(self) -> int:
        """Get the number of items processed so far."""
        return self._processed_count
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type:
            self.cancel()
        
        # Force garbage collection on exit
        gc.collect()


class ChunkedStreamingProcessor(StreamingProcessor):
    """
    Chunked streaming processor with advanced memory management.
    
    This processor uses chunked processing with automatic memory monitoring
    and dynamic batch size adjustment.
    """
    
    def __init__(
        self,
        config: Optional[BatchConfig] = None,
        chunk_size: int = 1000,
        max_memory_mb: Optional[int] = None
    ):
        """
        Initialize the chunked streaming processor.
        
        Args:
            config: Batch configuration (uses default if None)
            chunk_size: Size of chunks to process
            max_memory_mb: Maximum memory usage in MB
        """
        super().__init__(config, max_memory_mb=max_memory_mb)
        self.chunk_size = chunk_size
        self._chunk_count = 0
    
    async def stream_chunks(
        self,
        source: AsyncIterator[Any],
        chunk_size: Optional[int] = None
    ) -> AsyncIterator[List[Any]]:
        """
        Stream items in chunks with memory monitoring.
        
        Args:
            source: Async iterator of items
            chunk_size: Size of chunks (overrides config)
            
        Yields:
            List of items in each chunk
        """
        chunk_size = chunk_size or self.chunk_size
        current_chunk = []
        
        async for item in source:
            if self.is_cancelled():
                break
            
            current_chunk.append(item)
            
            # Yield chunk when it reaches the desired size
            if len(current_chunk) >= chunk_size:
                yield current_chunk
                current_chunk = []
                self._chunk_count += 1
                
                # Monitor memory usage
                memory_usage = self.memory_monitor.get_memory_usage_mb()
                if self.config.max_memory_mb and memory_usage > self.config.max_memory_mb:
                    logger.warning(f"Memory usage {memory_usage:.1f}MB exceeds limit")
                    # Force garbage collection
                    gc.collect()
        
        # Yield remaining items
        if current_chunk and not self.is_cancelled():
            yield current_chunk
            self._chunk_count += 1
    
    def get_chunk_count(self) -> int:
        """Get the number of chunks processed."""
        return self._chunk_count







