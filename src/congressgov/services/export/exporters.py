"""Format-specific exporters (CSV, Excel, JSON, Parquet, XML), each handling
its own formatting quirks and optimizations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
import csv
import json
import logging
from pathlib import Path

from .base import BaseExporter, ExportConfig, ExportFormat

logger = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    import openpyxl
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    openpyxl = None
    Workbook = None
    dataframe_to_rows = None

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    PYARROW_AVAILABLE = True
except ImportError:
    PYARROW_AVAILABLE = False
    pa = None
    pq = None


class CSVExporter(BaseExporter):
    """CSV exporter with configurable delimiter/quoting, encoding, optional
    header row, and chunked writing for large datasets.
    """
    
    def __init__(self, config: Optional[ExportConfig] = None):
        super().__init__(config)
        self.format = ExportFormat.CSV
    
    def export(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to CSV format.
        
        Args:
            data: Data to export
            filepath: Output CSV file path
            **kwargs: Additional CSV options
        """
        try:
            self._ensure_directory(filepath)
            processed_data = self._process_data(data)
            
            if not processed_data:
                self.logger.warning("No data to export")
                return
            
            self._log_export_start(filepath, len(processed_data))
            
            # Get CSV options from kwargs or config
            delimiter = kwargs.get('delimiter', self.config.csv_delimiter)
            quote_char = kwargs.get('quote_char', self.config.csv_quote_char)
            encoding = kwargs.get('encoding', self.config.encoding)
            
            with open(filepath, 'w', newline='', encoding=encoding) as csvfile:
                if processed_data:
                    fieldnames = processed_data[0].keys()
                    writer = csv.DictWriter(
                        csvfile,
                        fieldnames=fieldnames,
                        delimiter=delimiter,
                        quotechar=quote_char,
                        quoting=csv.QUOTE_MINIMAL
                    )
                    
                    # Write header
                    writer.writeheader()
                    
                    # Write data in chunks
                    chunk_size = self.config.get_chunk_size()
                    for i in range(0, len(processed_data), chunk_size):
                        chunk = processed_data[i:i + chunk_size]
                        writer.writerows(chunk)
                        
                        # Progress callback
                        if self.config.progress_callback:
                            self.config.progress_callback(i + len(chunk), len(processed_data))
            
            self._log_export_complete(filepath, len(processed_data))
            
        except Exception as e:
            self._log_export_error(filepath, e)
            raise


class ExcelExporter(BaseExporter):
    """Excel exporter with multi-sheet support, custom sheet names, and formatting options."""
    
    def __init__(self, config: Optional[ExportConfig] = None):
        super().__init__(config)
        self.format = ExportFormat.EXCEL
        
        if not OPENPYXL_AVAILABLE:
            raise ImportError(
                "openpyxl is required for Excel export. Install with: pip install openpyxl"
            )
    
    def export(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to Excel format.
        
        Args:
            data: Data to export
            filepath: Output Excel file path
            **kwargs: Additional Excel options
                - sheets: Dict of {sheet_name: data} for multiple sheets
                - sheet_name: Single sheet name
        """
        try:
            self._ensure_directory(filepath)
            
            # Handle multiple sheets
            sheets = kwargs.get('sheets')
            if sheets:
                self._export_multiple_sheets(sheets, filepath, **kwargs)
            else:
                self._export_single_sheet(data, filepath, **kwargs)
                
        except Exception as e:
            self._log_export_error(filepath, e)
            raise
    
    def _export_single_sheet(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """Export data to a single Excel sheet."""
        processed_data = self._process_data(data)
        
        if not processed_data:
            self.logger.warning("No data to export")
            return
        
        self._log_export_start(filepath, len(processed_data))
        
        # Create workbook and worksheet
        wb = Workbook()
        ws = wb.active
        sheet_name = kwargs.get('sheet_name', self.config.excel_sheet_name)
        ws.title = sheet_name
        
        # Write headers
        if processed_data:
            headers = list(processed_data[0].keys())
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            
            # Write data
            for row, record in enumerate(processed_data, 2):
                for col, (key, value) in enumerate(record.items(), 1):
                    ws.cell(row=row, column=col, value=value)
        
        # Save workbook
        wb.save(filepath)
        self._log_export_complete(filepath, len(processed_data))
    
    def _export_multiple_sheets(self, sheets: Dict[str, Any], filepath: Union[str, Path], **kwargs) -> None:
        """Export multiple sheets to Excel."""
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        total_records = 0
        for sheet_name, sheet_data in sheets.items():
            processed_data = self._process_data(sheet_data)
            if not processed_data:
                continue
            
            # Create worksheet
            ws = wb.create_sheet(title=sheet_name)
            
            # Write headers
            headers = list(processed_data[0].keys())
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            
            # Write data
            for row, record in enumerate(processed_data, 2):
                for col, (key, value) in enumerate(record.items(), 1):
                    ws.cell(row=row, column=col, value=value)
            
            total_records += len(processed_data)
        
        # Save workbook
        wb.save(filepath)
        self._log_export_complete(filepath, total_records)


class JSONExporter(BaseExporter):
    """JSON exporter with pretty-printing, key sorting, and custom separators."""
    
    def __init__(self, config: Optional[ExportConfig] = None):
        super().__init__(config)
        self.format = ExportFormat.JSON
    
    def export(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to JSON format.
        
        Args:
            data: Data to export
            filepath: Output JSON file path
            **kwargs: Additional JSON options
                - indent: JSON indentation level
                - sort_keys: Sort JSON keys
                - separators: JSON separators
        """
        try:
            self._ensure_directory(filepath)
            processed_data = self._process_data(data)
            
            if not processed_data:
                self.logger.warning("No data to export")
                return
            
            self._log_export_start(filepath, len(processed_data))
            
            # Get JSON options
            indent = kwargs.get('indent', self.config.json_indent)
            sort_keys = kwargs.get('sort_keys', self.config.json_sort_keys)
            separators = kwargs.get('separators', (',', ':'))
            encoding = kwargs.get('encoding', self.config.encoding)
            
            # Write JSON
            with open(filepath, 'w', encoding=encoding) as jsonfile:
                json.dump(
                    processed_data,
                    jsonfile,
                    indent=indent,
                    sort_keys=sort_keys,
                    separators=separators,
                    ensure_ascii=False
                )
            
            self._log_export_complete(filepath, len(processed_data))
            
        except Exception as e:
            self._log_export_error(filepath, e)
            raise


class ParquetExporter(BaseExporter):
    """Parquet exporter with columnar storage, compression, and schema preservation."""
    
    def __init__(self, config: Optional[ExportConfig] = None):
        super().__init__(config)
        self.format = ExportFormat.PARQUET
        
        if not PYARROW_AVAILABLE:
            raise ImportError(
                "pyarrow is required for Parquet export. Install with: pip install pyarrow"
            )
    
    def export(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to Parquet format.
        
        Args:
            data: Data to export
            filepath: Output Parquet file path
            **kwargs: Additional Parquet options
                - compression: Compression algorithm
                - schema: PyArrow schema
        """
        try:
            self._ensure_directory(filepath)
            processed_data = self._process_data(data)
            
            if not processed_data:
                self.logger.warning("No data to export")
                return
            
            self._log_export_start(filepath, len(processed_data))
            
            # Convert to PyArrow Table
            if PANDAS_AVAILABLE:
                # Use pandas for better type inference
                df = pd.DataFrame(processed_data)
                table = pa.Table.from_pandas(df)
            else:
                # Convert directly to PyArrow Table
                table = pa.Table.from_pydict({
                    key: [record.get(key) for record in processed_data]
                    for key in processed_data[0].keys()
                })
            
            # Get Parquet options
            compression = kwargs.get('compression', 'snappy')
            schema = kwargs.get('schema')
            
            # Write Parquet file (omit schema= when None — PyArrow 18+ errors if duplicated)
            if schema is not None:
                pq.write_table(table, filepath, compression=compression, schema=schema)
            else:
                pq.write_table(table, filepath, compression=compression)
            
            self._log_export_complete(filepath, len(processed_data))
            
        except Exception as e:
            self._log_export_error(filepath, e)
            raise


class TSVExporter(CSVExporter):
    """
    Tab-separated values exporter (extends CSVExporter).
    """
    
    def __init__(self, config: Optional[ExportConfig] = None):
        super().__init__(config)
        self.config.csv_delimiter = '\t'
        self.format = ExportFormat.TSV


class XMLExporter(BaseExporter):
    """XML exporter with configurable root/item element names, attributes, and pretty printing."""
    
    def __init__(self, config: Optional[ExportConfig] = None):
        super().__init__(config)
        self.format = ExportFormat.XML
    
    def export(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Export data to XML format.
        
        Args:
            data: Data to export
            filepath: Output XML file path
            **kwargs: Additional XML options
                - root_name: Root element name
                - item_name: Item element name
                - pretty_print: Enable pretty printing
        """
        try:
            self._ensure_directory(filepath)
            processed_data = self._process_data(data)
            
            if not processed_data:
                self.logger.warning("No data to export")
                return
            
            self._log_export_start(filepath, len(processed_data))
            
            # Get XML options
            root_name = kwargs.get('root_name', 'data')
            item_name = kwargs.get('item_name', 'item')
            pretty_print = kwargs.get('pretty_print', True)
            encoding = kwargs.get('encoding', self.config.encoding)
            
            # Generate XML
            xml_content = self._generate_xml(
                processed_data,
                root_name,
                item_name,
                pretty_print
            )
            
            # Write XML file
            with open(filepath, 'w', encoding=encoding) as xmlfile:
                xmlfile.write(xml_content)
            
            self._log_export_complete(filepath, len(processed_data))
            
        except Exception as e:
            self._log_export_error(filepath, e)
            raise
    
    def _generate_xml(self, data: List[Dict[str, Any]], root_name: str, item_name: str, pretty_print: bool) -> str:
        """Generate XML content from data."""
        import xml.etree.ElementTree as ET
        
        root = ET.Element(root_name)
        
        for record in data:
            item = ET.SubElement(root, item_name)
            for key, value in record.items():
                # Create element for each field
                field = ET.SubElement(item, key)
                field.text = str(value) if value is not None else ""
        
        # Convert to string
        if pretty_print:
            self._indent_xml(root)
        
        return ET.tostring(root, encoding='unicode')
    
    def _indent_xml(self, elem, level=0):
        """Add indentation to XML for pretty printing."""
        indent = "\n" + level * "  "
        if len(elem):
            if not elem.text or elem.text.isspace():
                elem.text = indent + "  "
            if not elem.tail or elem.tail.isspace():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or child.tail.isspace():
                child.tail = indent
        else:
            if level and (not elem.tail or elem.tail.isspace()):
                elem.tail = indent







