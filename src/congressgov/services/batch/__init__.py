"""
Batch operations and bulk processing for congressgov: parallel processing
with configurable concurrency, memory-efficient streaming for large
datasets, error handling/recovery, progress tracking, and checkpoint/resume,
all built on the existing async infrastructure.

Usage:
    from congressgov.services.batch import BatchProcessor, StreamingProcessor, BatchMonitor
    from congressgov.services.async_api import AsyncBill
    from tqdm import tqdm
    
    # Basic batch processing
    batch_processor = BatchProcessor(max_concurrent=10, batch_size=50)
    bills = await batch_processor.bulk_fetch(bill_service.get, params_list)
    
    # Streaming large datasets
    streaming_processor = StreamingProcessor(batch_size=100, max_memory_mb=1000)
    async for batch in streaming_processor.stream_items(data_source):
        await process_batch(batch)
"""

# Core batch processing
from .base import BatchConfig, BatchResult, BaseBatchProcessor
from .processor import BatchProcessor
from .parallel import ParallelProcessor

# Streaming and memory management
from .streaming import StreamingProcessor
from .memory import MemoryMonitor
from .checkpoint import CheckpointManager

# Error handling and recovery
from .resilient import ResilientBatchProcessor
from .recovery import ErrorRecoveryManager
from .circuit_breaker import CircuitBreaker

# Monitoring and analytics
from .monitor import BatchMonitor
from .analytics import BatchAnalytics
from .reporting import BatchReporter

__all__ = [
    # Core batch processing
    'BatchConfig',
    'BatchResult',
    'BaseBatchProcessor',
    'BatchProcessor',
    'ParallelProcessor',
    
    # Streaming and memory management
    'StreamingProcessor',
    'MemoryMonitor',
    'CheckpointManager',
    
    # Error handling and recovery
    'ResilientBatchProcessor',
    'ErrorRecoveryManager',
    'CircuitBreaker',
    
    # Monitoring and analytics
    'BatchMonitor',
    'BatchAnalytics',
    'BatchReporter',
]







