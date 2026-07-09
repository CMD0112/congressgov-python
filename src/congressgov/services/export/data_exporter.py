"""
Unified data exporter facade.

This module provides a single interface for all data export operations,
automatically detecting the appropriate exporter based on file extension
and providing a consistent API across all formats.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Callable
import logging
from pathlib import Path

from .base import BaseExporter, ExportConfig, ExportFormat
from .exporters import (
    CSVExporter, ExcelExporter, JSONExporter, ParquetExporter,
    TSVExporter, XMLExporter
)

logger = logging.getLogger(__name__)


class DataExporter:
    """
    Unified data exporter with automatic format detection.
    
    This class provides a single interface for exporting data to various
    formats, automatically selecting the appropriate exporter based on
    the file extension.
    
    Example:
        exporter = DataExporter()
        exporter.to_csv(data, "output.csv")
        exporter.to_excel(data, "output.xlsx")
        exporter.to_json(data, "output.json")
    """
    
    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Initialize the data exporter.
        
        Args:
            config: Export configuration (uses default if None)
        """
        self.config = config or ExportConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize exporters lazily to handle missing dependencies
        self._exporters = {}
    
    def _get_exporter(self, format_type: ExportFormat) -> BaseExporter:
        """Get exporter for format, initializing if needed."""
        if format_type not in self._exporters:
            if format_type == ExportFormat.CSV:
                self._exporters[format_type] = CSVExporter(self.config)
            elif format_type == ExportFormat.EXCEL:
                self._exporters[format_type] = ExcelExporter(self.config)
            elif format_type == ExportFormat.JSON:
                self._exporters[format_type] = JSONExporter(self.config)
            elif format_type == ExportFormat.PARQUET:
                self._exporters[format_type] = ParquetExporter(self.config)
            elif format_type == ExportFormat.TSV:
                self._exporters[format_type] = TSVExporter(self.config)
            elif format_type == ExportFormat.XML:
                self._exporters[format_type] = XMLExporter(self.config)
        
        return self._exporters[format_type]
    
    def to_csv(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to CSV format.
        
        Args:
            data: Data to export
            filepath: Output CSV file path
            **kwargs: Additional CSV options
        """
        self._export(ExportFormat.CSV, data, filepath, **kwargs)
    
    def to_excel(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to Excel format.
        
        Args:
            data: Data to export
            filepath: Output Excel file path
            **kwargs: Additional Excel options
                - sheets: Dict of {sheet_name: data} for multiple sheets
                - sheet_name: Single sheet name
        """
        self._export(ExportFormat.EXCEL, data, filepath, **kwargs)
    
    def to_json(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to JSON format.
        
        Args:
            data: Data to export
            filepath: Output JSON file path
            **kwargs: Additional JSON options
                - indent: JSON indentation level
                - sort_keys: Sort JSON keys
        """
        self._export(ExportFormat.JSON, data, filepath, **kwargs)
    
    def to_parquet(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to Parquet format.
        
        Args:
            data: Data to export
            filepath: Output Parquet file path
            **kwargs: Additional Parquet options
                - compression: Compression algorithm
        """
        self._export(ExportFormat.PARQUET, data, filepath, **kwargs)
    
    def to_tsv(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to TSV (Tab-Separated Values) format.
        
        Args:
            data: Data to export
            filepath: Output TSV file path
            **kwargs: Additional TSV options
        """
        self._export(ExportFormat.TSV, data, filepath, **kwargs)
    
    def to_xml(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to XML format.
        
        Args:
            data: Data to export
            filepath: Output XML file path
            **kwargs: Additional XML options
                - root_name: Root element name
                - item_name: Item element name
        """
        self._export(ExportFormat.XML, data, filepath, **kwargs)
    
    def export(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data with automatic format detection.
        
        Args:
            data: Data to export
            filepath: Output file path (format detected from extension)
            **kwargs: Additional export options
        """
        filepath = Path(filepath)
        extension = filepath.suffix.lower()
        
        # Map extensions to formats
        extension_map = {
            '.csv': ExportFormat.CSV,
            '.xlsx': ExportFormat.EXCEL,
            '.xls': ExportFormat.EXCEL,
            '.json': ExportFormat.JSON,
            '.parquet': ExportFormat.PARQUET,
            '.tsv': ExportFormat.TSV,
            '.xml': ExportFormat.XML,
        }
        
        format_type = extension_map.get(extension)
        if not format_type:
            raise ValueError(f"Unsupported file format: {extension}")
        
        self._export(format_type, data, filepath, **kwargs)
    
    def _export(self, format_type: ExportFormat, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Internal export method.
        
        Args:
            format_type: Export format
            data: Data to export
            filepath: Output file path
            **kwargs: Additional export options
        """
        try:
            exporter = self._get_exporter(format_type)
            
            # Update exporter config with any new settings
            if kwargs:
                exporter.config = self._merge_config(exporter.config, kwargs)
            
            exporter.export(data, filepath, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Export failed for {filepath}: {e}")
            raise
    
    def _merge_config(self, base_config: ExportConfig, kwargs: Dict[str, Any]) -> ExportConfig:
        """
        Merge additional configuration with base config.
        
        Args:
            base_config: Base export configuration
            kwargs: Additional configuration options
            
        Returns:
            Merged configuration
        """
        # Create a copy of the base config
        merged_config = ExportConfig(
            format=base_config.format,
            encoding=base_config.encoding,
            include_index=base_config.include_index,
            flatten_nested=base_config.flatten_nested,
            max_depth=base_config.max_depth,
            handle_missing=base_config.handle_missing,
            missing_value=base_config.missing_value,
            chunk_size=base_config.chunk_size,
            use_generators=base_config.use_generators,
            progress_callback=base_config.progress_callback,
            validate_data=base_config.validate_data,
            strict_mode=base_config.strict_mode,
            csv_delimiter=base_config.csv_delimiter,
            csv_quote_char=base_config.csv_quote_char,
            excel_sheet_name=base_config.excel_sheet_name,
            json_indent=base_config.json_indent,
            json_sort_keys=base_config.json_sort_keys,
            field_mappings=base_config.field_mappings.copy(),
            exclude_fields=base_config.exclude_fields.copy(),
            include_fields=base_config.include_fields.copy() if base_config.include_fields else None
        )
        
        # Update with kwargs
        for key, value in kwargs.items():
            if hasattr(merged_config, key):
                setattr(merged_config, key, value)
        
        return merged_config
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported export formats.
        
        Returns:
            List of supported format extensions
        """
        return ['.csv', '.xlsx', '.xls', '.json', '.parquet', '.tsv', '.xml']
    
    def is_format_supported(self, filepath: Union[str, Path]) -> bool:
        """
        Check if a file format is supported.
        
        Args:
            filepath: File path to check
            
        Returns:
            True if format is supported
        """
        extension = Path(filepath).suffix.lower()
        return extension in self.get_supported_formats()
    
    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """
        Set progress callback for export operations.
        
        Args:
            callback: Function to call with (current, total) progress
        """
        self.config.progress_callback = callback
        
        # Update all exporters
        for exporter in self._exporters.values():
            exporter.config.progress_callback = callback
    
    def set_config(self, config: ExportConfig) -> None:
        """
        Update export configuration.
        
        Args:
            config: New export configuration
        """
        self.config = config
        
        # Update all exporters
        for exporter in self._exporters.values():
            exporter.config = config
    
    def get_config(self) -> ExportConfig:
        """
        Get current export configuration.
        
        Returns:
            Current export configuration
        """
        return self.config
    
    def validate_data(self, data: Any) -> bool:
        """
        Validate data before export.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid for export
        """
        try:
            if data is None:
                return False
            if isinstance(data, (list, tuple)) and len(data) == 0:
                return False
            # Use CSV exporter for validation (most permissive)
            csv_exporter = self._get_exporter(ExportFormat.CSV)
            csv_exporter._process_data(data)
            return True
        except Exception as e:
            self.logger.warning(f"Data validation failed: {e}")
            return False
    
    def get_data_info(self, data: Any) -> Dict[str, Any]:
        """
        Get information about the data to be exported.
        
        Args:
            data: Data to analyze
            
        Returns:
            Dictionary with data information
        """
        try:
            processed_data = self._get_exporter(ExportFormat.CSV)._process_data(data)
            
            if not processed_data:
                return {
                    'record_count': 0,
                    'fields': [],
                    'field_count': 0
                }
            
            fields = list(processed_data[0].keys())
            return {
                'record_count': len(processed_data),
                'fields': fields,
                'field_count': len(fields),
                'sample_record': processed_data[0] if processed_data else None
            }
        except Exception as e:
            self.logger.warning(f"Failed to analyze data: {e}")
            return {
                'record_count': 0,
                'fields': [],
                'field_count': 0,
                'error': str(e)
            }
