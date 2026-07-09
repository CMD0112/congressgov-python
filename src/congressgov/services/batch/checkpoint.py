"""
Checkpoint system for batch operations.

This module provides checkpoint management for saving and resuming batch
processing progress, enabling recovery from failures and interruptions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from .base import BatchResult, BatchStatus

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Checkpoint manager for batch operations.
    
    This class provides comprehensive checkpoint management including saving,
    loading, and resuming batch processing progress.
    
    Example:
        manager = CheckpointManager(
            checkpoint_file="./checkpoints/bill_processing.json",
            save_interval=1000
        )
        
        # Save checkpoint
        await manager.save_checkpoint({
            'processed_count': 5000,
            'last_item': 'hr-123',
            'result': batch_result.to_dict()
        })
        
        # Load checkpoint
        checkpoint = await manager.load_checkpoint()
        if checkpoint:
            # Resume from checkpoint
            start_from = checkpoint['processed_count']
    """
    
    def __init__(
        self,
        checkpoint_file: Optional[Union[str, Path]] = None,
        save_interval: int = 1000,
        max_checkpoints: int = 10,
        auto_cleanup: bool = True
    ):
        """
        Initialize the checkpoint manager.
        
        Args:
            checkpoint_file: Path to checkpoint file
            save_interval: Interval for automatic checkpoint saving
            max_checkpoints: Maximum number of checkpoints to keep
            auto_cleanup: Whether to automatically clean up old checkpoints
        """
        self.checkpoint_file = Path(checkpoint_file) if checkpoint_file else None
        self.save_interval = save_interval
        self.max_checkpoints = max_checkpoints
        self.auto_cleanup = auto_cleanup
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self._last_save_time = None
        self._checkpoint_count = 0
        
        # Create checkpoint directory if needed
        if self.checkpoint_file:
            self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
    
    async def save_checkpoint(
        self,
        state: Dict[str, Any],
        checkpoint_file: Optional[Union[str, Path]] = None
    ) -> bool:
        """
        Save a checkpoint with the current state.
        
        Args:
            state: State dictionary to save
            checkpoint_file: Optional override for checkpoint file
            
        Returns:
            True if checkpoint was saved successfully
        """
        file_path = checkpoint_file or self.checkpoint_file
        if not file_path:
            self.logger.warning("No checkpoint file specified")
            return False
        
        try:
            # Add metadata to state
            checkpoint_data = {
                'state': state,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'checkpoint_count': self._checkpoint_count,
                    'version': '1.0'
                }
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2, default=str)
            
            self._last_save_time = datetime.now()
            self._checkpoint_count += 1
            
            self.logger.debug(f"Checkpoint saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")
            return False
    
    async def load_checkpoint(
        self,
        checkpoint_file: Optional[Union[str, Path]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load the most recent checkpoint.
        
        Args:
            checkpoint_file: Optional override for checkpoint file
            
        Returns:
            Checkpoint state or None if not found
        """
        file_path = checkpoint_file or self.checkpoint_file
        if not file_path or not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Validate checkpoint format
            if 'state' not in checkpoint_data:
                self.logger.warning("Invalid checkpoint format: missing 'state'")
                return None
            
            self.logger.debug(f"Checkpoint loaded from {file_path}")
            return checkpoint_data['state']
            
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")
            return None
    
    async def clear_checkpoint(
        self,
        checkpoint_file: Optional[Union[str, Path]] = None
    ) -> bool:
        """
        Clear the checkpoint file.
        
        Args:
            checkpoint_file: Optional override for checkpoint file
            
        Returns:
            True if checkpoint was cleared successfully
        """
        file_path = checkpoint_file or self.checkpoint_file
        if not file_path or not file_path.exists():
            return True
        
        try:
            file_path.unlink()
            self.logger.debug(f"Checkpoint cleared: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear checkpoint: {e}")
            return False
    
    def get_progress(self, state: Optional[Dict[str, Any]] = None) -> float:
        """
        Get progress percentage from state.
        
        Args:
            state: State dictionary (loads from file if None)
            
        Returns:
            Progress percentage (0.0-100.0)
        """
        if state is None:
            state = asyncio.run(self.load_checkpoint())
        
        if not state:
            return 0.0
        
        processed_count = state.get('processed_count', 0)
        total_count = state.get('total_count', 0)
        
        if total_count == 0:
            return 0.0
        
        return min(100.0, (processed_count / total_count) * 100.0)
    
    def should_save_checkpoint(self, processed_count: int) -> bool:
        """
        Check if a checkpoint should be saved based on interval.
        
        Args:
            processed_count: Number of items processed so far
            
        Returns:
            True if checkpoint should be saved
        """
        return (
            self.save_interval > 0 and
            processed_count > 0 and
            processed_count % self.save_interval == 0
        )
    
    def get_checkpoint_info(self) -> Dict[str, Any]:
        """
        Get information about the current checkpoint.
        
        Returns:
            Dictionary with checkpoint information
        """
        if not self.checkpoint_file or not self.checkpoint_file.exists():
            return {
                'exists': False,
                'file_path': str(self.checkpoint_file) if self.checkpoint_file else None
            }
        
        try:
            stat = self.checkpoint_file.stat()
            return {
                'exists': True,
                'file_path': str(self.checkpoint_file),
                'size_bytes': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'checkpoint_count': self._checkpoint_count,
                'last_save_time': self._last_save_time.isoformat() if self._last_save_time else None
            }
        except Exception as e:
            self.logger.error(f"Failed to get checkpoint info: {e}")
            return {
                'exists': False,
                'error': str(e)
            }
    
    async def cleanup_old_checkpoints(self) -> int:
        """
        Clean up old checkpoint files.
        
        Returns:
            Number of checkpoints cleaned up
        """
        if not self.auto_cleanup or not self.checkpoint_file:
            return 0
        
        try:
            checkpoint_dir = self.checkpoint_file.parent
            checkpoint_files = list(checkpoint_dir.glob(f"{self.checkpoint_file.stem}*.json"))
            
            if len(checkpoint_files) <= self.max_checkpoints:
                return 0
            
            # Sort by modification time (oldest first)
            checkpoint_files.sort(key=lambda f: f.stat().st_mtime)
            
            # Remove oldest checkpoints
            files_to_remove = checkpoint_files[:-self.max_checkpoints]
            removed_count = 0
            
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    removed_count += 1
                    self.logger.debug(f"Removed old checkpoint: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove checkpoint {file_path}: {e}")
            
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old checkpoints")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old checkpoints: {e}")
            return 0


class BatchCheckpointManager(CheckpointManager):
    """
    Specialized checkpoint manager for batch operations.
    
    This class extends the base checkpoint manager with batch-specific
    functionality including progress tracking and result management.
    """
    
    def __init__(
        self,
        checkpoint_file: Optional[Union[str, Path]] = None,
        save_interval: int = 1000,
        **kwargs
    ):
        """
        Initialize the batch checkpoint manager.
        
        Args:
            checkpoint_file: Path to checkpoint file
            save_interval: Interval for automatic checkpoint saving
            **kwargs: Additional arguments for base class
        """
        super().__init__(checkpoint_file, save_interval, **kwargs)
        self._batch_results: List[BatchResult] = []
    
    async def save_batch_result(
        self,
        result: BatchResult,
        additional_state: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a batch result as a checkpoint.
        
        Args:
            result: Batch result to save
            additional_state: Additional state to include
            
        Returns:
            True if checkpoint was saved successfully
        """
        state = {
            'batch_result': result.to_dict(),
            'processed_count': result.processed_items,
            'successful_count': result.successful_items,
            'failed_count': result.failed_items,
            'status': result.status.value,
            'timestamp': datetime.now().isoformat()
        }
        
        if additional_state:
            state.update(additional_state)
        
        return await self.save_checkpoint(state)
    
    async def load_batch_result(self) -> Optional[BatchResult]:
        """
        Load the most recent batch result from checkpoint.
        
        Returns:
            BatchResult or None if not found
        """
        state = await self.load_checkpoint()
        if not state or 'batch_result' not in state:
            return None
        
        try:
            # Reconstruct BatchResult from saved data
            result_data = state['batch_result']
            result = BatchResult()
            
            # Restore basic properties
            result.total_items = result_data.get('total_items', 0)
            result.processed_items = result_data.get('processed_items', 0)
            result.successful_items = result_data.get('successful_items', 0)
            result.failed_items = result_data.get('failed_items', 0)
            result.retried_items = result_data.get('retried_items', 0)
            
            # Restore timing
            if result_data.get('start_time'):
                result.start_time = datetime.fromisoformat(result_data['start_time'])
            if result_data.get('end_time'):
                result.end_time = datetime.fromisoformat(result_data['end_time'])
            if result_data.get('duration_seconds'):
                result.duration = timedelta(seconds=result_data['duration_seconds'])
            
            # Restore status
            status_value = result_data.get('status', 'pending')
            result.status = BatchStatus(status_value)
            result.cancelled = result_data.get('cancelled', False)
            
            # Restore performance metrics
            result.items_per_second = result_data.get('items_per_second', 0.0)
            result.memory_peak_mb = result_data.get('memory_peak_mb', 0.0)
            result.api_calls_made = result_data.get('api_calls_made', 0)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to reconstruct BatchResult: {e}")
            return None
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all processing results.
        
        Returns:
            Dictionary with processing summary
        """
        if not self._batch_results:
            return {
                'total_batches': 0,
                'total_processed': 0,
                'total_successful': 0,
                'total_failed': 0,
                'overall_success_rate': 0.0
            }
        
        total_processed = sum(result.processed_items for result in self._batch_results)
        total_successful = sum(result.successful_items for result in self._batch_results)
        total_failed = sum(result.failed_items for result in self._batch_results)
        
        return {
            'total_batches': len(self._batch_results),
            'total_processed': total_processed,
            'total_successful': total_successful,
            'total_failed': total_failed,
            'overall_success_rate': (total_successful / total_processed * 100.0) if total_processed > 0 else 0.0,
            'last_batch_time': self._batch_results[-1].start_time.isoformat() if self._batch_results else None
        }







