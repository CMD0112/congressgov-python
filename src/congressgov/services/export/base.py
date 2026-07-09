"""Shared export infrastructure: `ExportConfig`, `BaseExporter`, and serialization helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""
    
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"
    PARQUET = "parquet"
    TSV = "tsv"
    XML = "xml"


@dataclass
class ExportConfig:
    """Settings shared by all exporters: formatting, validation, and performance knobs."""
    
    # File format settings
    format: ExportFormat = ExportFormat.CSV
    encoding: str = "utf-8"
    include_index: bool = False
    
    # Data processing settings
    flatten_nested: bool = True
    max_depth: int = 10
    handle_missing: str = "skip"  # "skip", "fill", "error"
    missing_value: Any = None
    
    # Performance settings
    chunk_size: int = 1000
    use_generators: bool = True
    progress_callback: Optional[Callable[[int, int], None]] = None
    
    # Validation settings
    validate_data: bool = True
    strict_mode: bool = False
    
    # Format-specific settings
    csv_delimiter: str = ","
    csv_quote_char: str = '"'
    excel_sheet_name: str = "Data"
    json_indent: int = 2
    json_sort_keys: bool = False
    
    # Custom field mappings
    field_mappings: Dict[str, str] = field(default_factory=dict)
    exclude_fields: List[str] = field(default_factory=list)
    include_fields: Optional[List[str]] = None
    
    def get_missing_handling(self) -> str:
        """Get the missing value handling strategy."""
        return self.handle_missing
    
    def should_flatten(self) -> bool:
        """Check if nested data should be flattened."""
        return self.flatten_nested
    
    def get_chunk_size(self) -> int:
        """Get the chunk size for processing large datasets."""
        return self.chunk_size


class DataSerializable(Protocol):
    """Protocol for objects that can be serialized for export."""
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Serialize the object to a dictionary."""
        ...


class BaseExporter(ABC):
    """Base class for exporters: handles serialization, validation, and error handling."""
    
    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Initialize the exporter.
        
        Args:
            config: Export configuration (uses default if None)
        """
        self.config = config or ExportConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def export(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to the specified file.
        
        Args:
            data: Data to export
            filepath: Output file path
            **kwargs: Additional export options
        """
        pass
    
    def _serialize_data(self, data: Any) -> List[Dict[str, Any]]:
        """
        Serialize data for export.
        
        Args:
            data: Data to serialize
            
        Returns:
            List of serialized dictionaries
        """
        try:
            # Handle single objects
            if hasattr(data, 'model_dump'):
                return [data.model_dump()]
            
            # Handle collections
            if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                serialized = []
                for item in data:
                    if hasattr(item, 'model_dump'):
                        serialized.append(item.model_dump())
                    elif isinstance(item, dict):
                        serialized.append(item)
                    else:
                        # Convert to dict if possible
                        serialized.append(self._object_to_dict(item))
                return serialized
            
            # Handle dictionaries
            if isinstance(data, dict):
                return [data]
            
            # Fallback: convert to dict
            return [self._object_to_dict(data)]
            
        except Exception as e:
            self.logger.error(f"Failed to serialize data: {e}")
            raise ValueError(f"Unable to serialize data for export: {e}")
    
    def _object_to_dict(self, obj: Any) -> Dict[str, Any]:
        """
        Convert an object to a dictionary.
        
        Args:
            obj: Object to convert
            
        Returns:
            Dictionary representation
        """
        if isinstance(obj, dict):
            return obj
        
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        
        # Try to convert to dict using common methods
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        
        if hasattr(obj, 'dict'):
            return obj.dict()
        
        # Last resort: string representation
        return {"value": str(obj)}
    
    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
        """
        Flatten a nested dictionary.
        
        Args:
            data: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        if not self.config.should_flatten():
            return data
        
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict) and self._get_nesting_depth(data) < self.config.max_depth:
                items.extend(self._flatten_dict(value, new_key, sep).items())
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # Handle list of dictionaries
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        items.extend(self._flatten_dict(item, f"{new_key}_{i}", sep).items())
                    else:
                        items.append((f"{new_key}_{i}", item))
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    def _get_nesting_depth(self, data: Dict[str, Any], current_depth: int = 0) -> int:
        """Calculate the nesting depth of a dictionary."""
        if not isinstance(data, dict):
            return current_depth
        
        max_depth = current_depth
        for value in data.values():
            if isinstance(value, dict):
                depth = self._get_nesting_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate data before export.
        
        Args:
            data: Data to validate
            
        Returns:
            Validated data
        """
        if not self.config.validate_data:
            return data
        
        validated = []
        for i, item in enumerate(data):
            try:
                if not isinstance(item, dict):
                    raise ValueError(f"Item {i} is not a dictionary")
                
                # Check for required fields if specified
                if self.config.include_fields:
                    missing_fields = set(self.config.include_fields) - set(item.keys())
                    if missing_fields:
                        self.logger.warning(f"Item {i} missing fields: {missing_fields}")
                
                validated.append(item)
                
            except Exception as e:
                if self.config.strict_mode:
                    raise ValueError(f"Validation failed for item {i}: {e}")
                else:
                    self.logger.warning(f"Skipping invalid item {i}: {e}")
        
        return validated
    
    def _apply_field_mappings(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply field mappings to data.
        
        Args:
            data: Data to process
            
        Returns:
            Data with field mappings applied
        """
        if not self.config.field_mappings:
            return data
        
        mapped_data = []
        for item in data:
            mapped_item = {}
            for key, value in item.items():
                mapped_key = self.config.field_mappings.get(key, key)
                mapped_item[mapped_key] = value
            mapped_data.append(mapped_item)
        
        return mapped_data
    
    def _filter_fields(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter fields based on configuration.
        
        Args:
            data: Data to filter
            
        Returns:
            Filtered data
        """
        if not self.config.exclude_fields and not self.config.include_fields:
            return data
        
        filtered_data = []
        for item in data:
            filtered_item = {}
            for key, value in item.items():
                # Include field if it's in include_fields (if specified)
                if self.config.include_fields and key not in self.config.include_fields:
                    continue
                
                # Exclude field if it's in exclude_fields
                if key in self.config.exclude_fields:
                    continue
                
                filtered_item[key] = value
            
            filtered_data.append(filtered_item)
        
        return filtered_data
    
    def _handle_missing_values(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Handle missing values in data.
        
        Args:
            data: Data to process
            
        Returns:
            Data with missing values handled
        """
        if self.config.handle_missing == "skip":
            return data
        
        handled_data = []
        for item in data:
            handled_item = {}
            for key, value in item.items():
                if value is None or value == "":
                    if self.config.handle_missing == "fill":
                        handled_item[key] = self.config.missing_value
                    elif self.config.handle_missing == "error":
                        raise ValueError(f"Missing value for field '{key}'")
                    else:
                        handled_item[key] = value
                else:
                    handled_item[key] = value
            
            handled_data.append(handled_item)
        
        return handled_data
    
    def _process_data(self, data: Any) -> List[Dict[str, Any]]:
        """
        Process data through the complete pipeline.
        
        Args:
            data: Raw data to process
            
        Returns:
            Processed data ready for export
        """
        # Serialize data
        serialized = self._serialize_data(data)
        
        # Flatten nested structures
        if self.config.flatten_nested:
            flattened = []
            for item in serialized:
                flattened.append(self._flatten_dict(item))
            serialized = flattened
        
        # Apply field mappings
        mapped = self._apply_field_mappings(serialized)
        
        # Filter fields
        filtered = self._filter_fields(mapped)
        
        # Handle missing values
        handled = self._handle_missing_values(filtered)
        
        # Validate data
        validated = self._validate_data(handled)
        
        return validated
    
    def _ensure_directory(self, filepath: Union[str, Path]) -> None:
        """
        Ensure the directory for the filepath exists.
        
        Args:
            filepath: File path to check
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_file_extension(self, filepath: Union[str, Path]) -> str:
        """
        Get file extension from filepath.
        
        Args:
            filepath: File path
            
        Returns:
            File extension (without dot)
        """
        return Path(filepath).suffix.lstrip('.').lower()
    
    def _log_export_start(self, filepath: Union[str, Path], data_count: int) -> None:
        """Log the start of an export operation."""
        self.logger.info(f"Starting export to {filepath} ({data_count} records)")
    
    def _log_export_complete(self, filepath: Union[str, Path], data_count: int) -> None:
        """Log the completion of an export operation."""
        self.logger.info(f"Export completed: {filepath} ({data_count} records)")
    
    def _log_export_error(self, filepath: Union[str, Path], error: Exception) -> None:
        """Log an export error."""
        self.logger.error(f"Export failed for {filepath}: {error}")







