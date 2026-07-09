"""
Pandas integration for data export and analysis.

This module provides seamless integration with pandas DataFrames,
enabling easy conversion from congressgov models to
pandas DataFrames for data analysis and manipulation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Union
import logging
from pathlib import Path

# Optional pandas import with graceful fallback
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None
    np = None

from .base import ExportConfig

logger = logging.getLogger(__name__)


class PandasIntegration:
    """
    Pandas integration for congressgov.
    
    This class provides seamless conversion between congressgov
    models and pandas DataFrames, with automatic type inference and data
    cleaning capabilities.
    
    Example:
        pandas_int = PandasIntegration()
        bills = bill_service.search(congress=118, limit=100)
        df = pandas_int.to_dataframe(bills)
        
        # Perform analysis
        df['title_length'] = df['title'].str.len()
        df.groupby('type').size().plot(kind='bar')
    """
    
    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Initialize pandas integration.
        
        Args:
            config: Export configuration (uses default if None)
        """
        if not PANDAS_AVAILABLE:
            raise ImportError(
                "pandas is required for pandas integration. Install with: pip install pandas"
            )
        
        self.config = config or ExportConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def to_dataframe(self, data: Any, flatten: bool = True, **kwargs) -> 'pd.DataFrame':
        """
        Convert data to pandas DataFrame.
        
        Args:
            data: Data to convert (model, collection, or dict)
            flatten: Whether to flatten nested structures
            **kwargs: Additional conversion options
            
        Returns:
            pandas DataFrame
        """
        try:
            # Handle different data types
            collection_items = self._collection_items(data)
            if collection_items is not None:
                records = []
                for item in collection_items:
                    if hasattr(item, 'model_dump'):
                        records.append(item.model_dump())
                    elif isinstance(item, dict):
                        records.append(item)
                    else:
                        records.append(self._object_to_dict(item))
            elif hasattr(data, 'model_dump'):
                # Single Pydantic model (not a collection wrapper like Bills)
                records = [data.model_dump()]
            elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                # Plain iterable of models or dicts
                records = []
                for item in data:
                    if hasattr(item, 'model_dump'):
                        records.append(item.model_dump())
                    elif isinstance(item, dict):
                        records.append(item)
                    else:
                        records.append(self._object_to_dict(item))
            elif isinstance(data, dict):
                # Single dictionary
                records = [data]
            else:
                # Convert to dict
                records = [self._object_to_dict(data)]
            
            if not records:
                return pd.DataFrame()
            
            # Flatten nested structures if requested
            if flatten and self.config.flatten_nested:
                flattened_records = []
                for record in records:
                    flattened = self._flatten_dict(record)
                    flattened_records.append(flattened)
                records = flattened_records
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Apply data type optimizations
            df = self._optimize_dtypes(df)
            
            # Apply field mappings if specified
            if self.config.field_mappings:
                df = df.rename(columns=self.config.field_mappings)
            
            # Filter fields if specified
            if self.config.include_fields:
                available_fields = [col for col in self.config.include_fields if col in df.columns]
                df = df[available_fields]
            elif self.config.exclude_fields:
                df = df.drop(columns=self.config.exclude_fields, errors='ignore')
            
            # Handle missing values
            df = self._handle_missing_values(df)
            
            self.logger.info(f"Converted {len(df)} records to DataFrame with {len(df.columns)} columns")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to convert data to DataFrame: {e}")
            raise ValueError(f"Unable to convert data to DataFrame: {e}")
    
    def _collection_items(self, data: Any) -> list[Any] | None:
        """
        Return underlying items when data is a collection wrapper (e.g. Bills).

        Wrapper models are iterable (``__iter__``) but also have
        ``model_dump()``; they must not be serialized as a single row.
        """
        if isinstance(data, (str, bytes, dict)):
            return None

        if hasattr(data, '__iter__'):
            try:
                items = list(data)
            except TypeError:
                return None
            if not items and hasattr(data, 'model_dump'):
                return items
            if items and all(
                hasattr(item, 'model_dump') or isinstance(item, dict) for item in items
            ):
                return items

        return None

    def _object_to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert an object to a dictionary."""
        if isinstance(obj, dict):
            return obj
        
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        
        if hasattr(obj, 'dict'):
            return obj.dict()
        
        # Last resort: string representation
        return {"value": str(obj)}
    
    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
        """Flatten a nested dictionary."""
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
    
    def _optimize_dtypes(self, df: 'pd.DataFrame') -> 'pd.DataFrame':
        """Optimize DataFrame data types for memory efficiency."""
        try:
            # Convert object columns to appropriate types
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Try to convert to numeric
                    if self._is_numeric_column(df[col]):
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Try to convert to datetime
                    elif self._is_datetime_column(df[col]):
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    # Try to convert to category if low cardinality
                    elif self._should_categorize(df[col]):
                        df[col] = df[col].astype('category')
            
            # Convert integer columns to appropriate size
            for col in df.select_dtypes(include=['int64']).columns:
                if df[col].min() >= 0:
                    if df[col].max() < 255:
                        df[col] = df[col].astype('uint8')
                    elif df[col].max() < 65535:
                        df[col] = df[col].astype('uint16')
                    elif df[col].max() < 4294967295:
                        df[col] = df[col].astype('uint32')
                else:
                    if df[col].min() > -128 and df[col].max() < 127:
                        df[col] = df[col].astype('int8')
                    elif df[col].min() > -32768 and df[col].max() < 32767:
                        df[col] = df[col].astype('int16')
                    elif df[col].min() > -2147483648 and df[col].max() < 2147483647:
                        df[col] = df[col].astype('int32')
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Failed to optimize dtypes: {e}")
            return df
    
    def _is_numeric_column(self, series: 'pd.Series') -> bool:
        """Check if a column contains numeric data."""
        try:
            pd.to_numeric(series, errors='raise')
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_datetime_column(self, series: 'pd.Series') -> bool:
        """Check if a column contains datetime data."""
        if pd.api.types.is_datetime64_any_dtype(series):
            return True
        if not (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
        ):
            return False
        if series.isna().all():
            return False
        try:
            pd.to_datetime(series, errors='raise', format='mixed')
            return True
        except (ValueError, TypeError):
            return False
    
    def _should_categorize(self, series: 'pd.Series') -> bool:
        """Check if a column should be converted to category type."""
        # Convert to category if less than 50% unique values and not too many values
        unique_ratio = series.nunique() / len(series)
        return unique_ratio < 0.5 and series.nunique() < 1000
    
    def _handle_missing_values(self, df: 'pd.DataFrame') -> 'pd.DataFrame':
        """Handle missing values in DataFrame."""
        if self.config.handle_missing == "fill":
            df = df.fillna(self.config.missing_value)
        elif self.config.handle_missing == "skip":
            # Keep missing values as NaN
            pass
        elif self.config.handle_missing == "error":
            if df.isnull().any().any():
                raise ValueError("DataFrame contains missing values")
        
        return df
    
    def get_dataframe_info(self, df: 'pd.DataFrame') -> Dict[str, Any]:
        """
        Get comprehensive information about a DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with DataFrame information
        """
        try:
            info = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'unique_values': df.nunique().to_dict(),
                'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
                'categorical_columns': df.select_dtypes(include=['category']).columns.tolist(),
                'datetime_columns': df.select_dtypes(include=['datetime64']).columns.tolist(),
                'object_columns': df.select_dtypes(include=['object']).columns.tolist(),
            }
            
            # Add summary statistics for numeric columns
            if info['numeric_columns']:
                info['numeric_summary'] = df[info['numeric_columns']].describe().to_dict()
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get DataFrame info: {e}")
            return {'error': str(e)}
    
    def clean_dataframe(self, df: 'pd.DataFrame', **kwargs) -> 'pd.DataFrame':
        """
        Clean DataFrame with common data cleaning operations.
        
        Args:
            df: DataFrame to clean
            **kwargs: Cleaning options
                - remove_duplicates: Remove duplicate rows
                - remove_empty_rows: Remove rows with all NaN values
                - remove_empty_cols: Remove columns with all NaN values
                - standardize_text: Standardize text columns
                
        Returns:
            Cleaned DataFrame
        """
        try:
            cleaned_df = df.copy()
            
            # Remove duplicates
            if kwargs.get('remove_duplicates', True):
                cleaned_df = cleaned_df.drop_duplicates()
            
            # Remove empty rows
            if kwargs.get('remove_empty_rows', True):
                cleaned_df = cleaned_df.dropna(how='all')
            
            # Remove empty columns
            if kwargs.get('remove_empty_cols', True):
                cleaned_df = cleaned_df.dropna(axis=1, how='all')
            
            # Standardize text columns
            if kwargs.get('standardize_text', True):
                text_cols = cleaned_df.select_dtypes(include=['object']).columns
                for col in text_cols:
                    cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                    cleaned_df[col] = cleaned_df[col].replace('', np.nan)
            
            self.logger.info(f"Cleaned DataFrame: {df.shape} -> {cleaned_df.shape}")
            return cleaned_df
            
        except Exception as e:
            self.logger.error(f"Failed to clean DataFrame: {e}")
            return df
    
    def export_dataframe(self, df: 'pd.DataFrame', filepath: Union[str, Path], **kwargs) -> None:
        """
        Export DataFrame to various formats.
        
        Args:
            df: DataFrame to export
            filepath: Output file path
            **kwargs: Export options
        """
        try:
            filepath = Path(filepath)
            extension = filepath.suffix.lower()
            
            if extension == '.csv':
                df.to_csv(filepath, index=self.config.include_index, **kwargs)
            elif extension in ['.xlsx', '.xls']:
                try:
                    df.to_excel(filepath, index=self.config.include_index, **kwargs)
                except ImportError:
                    raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")
            elif extension == '.json':
                df.to_json(filepath, orient='records', indent=self.config.json_indent, **kwargs)
            elif extension == '.parquet':
                try:
                    df.to_parquet(filepath, **kwargs)
                except ImportError:
                    raise ImportError("pyarrow is required for Parquet export. Install with: pip install pyarrow")
            else:
                raise ValueError(f"Unsupported file format: {extension}")
            
            self.logger.info(f"Exported DataFrame to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to export DataFrame: {e}")
            raise
    
    def create_summary_report(self, df: 'pd.DataFrame') -> Dict[str, Any]:
        """
        Create a comprehensive summary report for a DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with summary report
        """
        try:
            report = {
                'basic_info': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                },
                'data_quality': {
                    'missing_values': df.isnull().sum().sum(),
                    'duplicate_rows': df.duplicated().sum(),
                    'completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                },
                'column_types': {
                    'numeric': len(df.select_dtypes(include=[np.number]).columns),
                    'categorical': len(df.select_dtypes(include=['category']).columns),
                    'datetime': len(df.select_dtypes(include=['datetime64']).columns),
                    'text': len(df.select_dtypes(include=['object']).columns),
                },
                'top_values': {}
            }
            
            # Get top values for each column
            for col in df.columns:
                if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                    top_values = df[col].value_counts().head(5).to_dict()
                    report['top_values'][col] = top_values
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to create summary report: {e}")
            return {'error': str(e)}
