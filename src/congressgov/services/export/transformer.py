"""
Data transformation pipeline for export operations.

This module provides a flexible data transformation system that allows
users to create complex data processing pipelines with chainable operations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable, Iterator
import logging
from abc import ABC, abstractmethod

# Optional pandas import
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from .base import ExportConfig

logger = logging.getLogger(__name__)


class TransformationStep(ABC):
    """Abstract base class for transformation steps."""
    
    @abstractmethod
    def apply(self, data: Any) -> Any:
        """Apply the transformation step."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the transformation step."""
        pass


class FunctionTransformationStep(TransformationStep):
    """Transformation step that applies a function."""
    
    def __init__(self, name: str, func: Callable[[Any], Any]):
        self.name = name
        self.func = func
    
    def apply(self, data: Any) -> Any:
        """Apply the transformation function."""
        return self.func(data)
    
    def get_name(self) -> str:
        """Get the step name."""
        return self.name


class DataTransformer:
    """
    Data transformation pipeline builder.
    
    This class provides a flexible way to create data transformation
    pipelines with chainable operations for cleaning, processing,
    and preparing data for export.
    
    Example:
        transformer = DataTransformer()
        
        pipeline = transformer.create_pipeline([
            ("clean_titles", lambda df: df.dropna(subset=['title'])),
            ("add_word_count", lambda df: df.assign(
                word_count=df['title'].str.split().str.len()
            )),
            ("filter_recent", lambda df: df[df['year'] >= 2020])
        ])
        
        transformed_data = pipeline.transform(bills)
    """
    
    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Initialize data transformer.
        
        Args:
            config: Export configuration (uses default if None)
        """
        self.config = config or ExportConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_pipeline(self, steps: List[tuple]) -> 'TransformationPipeline':
        """
        Create a transformation pipeline from steps.
        
        Args:
            steps: List of (name, function) tuples
            
        Returns:
            TransformationPipeline object
        """
        transformation_steps = []
        
        for name, func in steps:
            if not callable(func):
                raise ValueError(f"Step '{name}' must be callable")
            
            step = FunctionTransformationStep(name, func)
            transformation_steps.append(step)
        
        return TransformationPipeline(transformation_steps, self.config)
    
    def get_builtin_transformations(self) -> Dict[str, Callable]:
        """
        Get built-in transformation functions.
        
        Returns:
            Dictionary of built-in transformation functions
        """
        return {
            'remove_duplicates': self._remove_duplicates,
            'clean_text': self._clean_text,
            'normalize_dates': self._normalize_dates,
            'add_word_count': self._add_word_count,
            'add_title_length': self._add_title_length,
            'filter_recent': self._filter_recent,
            'filter_by_type': self._filter_by_type,
            'sort_by_date': self._sort_by_date,
            'sort_by_title': self._sort_by_title,
            'group_by_type': self._group_by_type,
            'sample_data': self._sample_data,
        }
    
    def _remove_duplicates(self, data: Any) -> Any:
        """Remove duplicate records."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            return data.drop_duplicates()
        elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
            seen = set()
            unique_data = []
            for item in data:
                item_hash = hash(str(item))
                if item_hash not in seen:
                    seen.add(item_hash)
                    unique_data.append(item)
            return unique_data
        return data
    
    def _clean_text(self, data: Any) -> Any:
        """Clean text fields."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            # Clean text columns
            text_cols = data.select_dtypes(include=['object']).columns
            for col in text_cols:
                data[col] = data[col].astype(str).str.strip()
                data[col] = data[col].replace('', pd.NA)
            return data
        return data
    
    def _normalize_dates(self, data: Any) -> Any:
        """Normalize date fields."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            # Find date columns
            date_cols = []
            for col in data.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    date_cols.append(col)
            
            # Convert to datetime
            for col in date_cols:
                try:
                    data[col] = pd.to_datetime(data[col], errors='coerce')
                except Exception:
                    pass
            
            return data
        return data
    
    def _add_word_count(self, data: Any) -> Any:
        """Add word count for text fields."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            # Find text columns
            text_cols = data.select_dtypes(include=['object']).columns
            for col in text_cols:
                if 'title' in col.lower() or 'text' in col.lower():
                    data[f'{col}_word_count'] = data[col].str.split().str.len()
            return data
        return data
    
    def _add_title_length(self, data: Any) -> Any:
        """Add title length for text fields."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            # Find title columns
            title_cols = [col for col in data.columns if 'title' in col.lower()]
            for col in title_cols:
                data[f'{col}_length'] = data[col].str.len()
            return data
        return data
    
    def _filter_recent(self, data: Any, year: int = 2020) -> Any:
        """Filter data to recent years."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            # Find date columns
            date_cols = [col for col in data.columns if 'date' in col.lower()]
            if date_cols:
                date_col = date_cols[0]
                data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
                return data[data[date_col].dt.year >= year]
        return data
    
    def _filter_by_type(self, data: Any, type_value: str) -> Any:
        """Filter data by type field."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            # Find type columns
            type_cols = [col for col in data.columns if 'type' in col.lower()]
            if type_cols:
                type_col = type_cols[0]
                return data[data[type_col] == type_value]
        return data
    
    def _sort_by_date(self, data: Any) -> Any:
        """Sort data by date."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            # Find date columns
            date_cols = [col for col in data.columns if 'date' in col.lower()]
            if date_cols:
                date_col = date_cols[0]
                data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
                return data.sort_values(date_col)
        return data
    
    def _sort_by_title(self, data: Any) -> Any:
        """Sort data by title."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            # Find title columns
            title_cols = [col for col in data.columns if 'title' in col.lower()]
            if title_cols:
                title_col = title_cols[0]
                return data.sort_values(title_col)
        return data
    
    def _group_by_type(self, data: Any) -> Any:
        """Group data by type."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            # Find type columns
            type_cols = [col for col in data.columns if 'type' in col.lower()]
            if type_cols:
                type_col = type_cols[0]
                return data.groupby(type_col)
        return data
    
    def _sample_data(self, data: Any, n: int = 100) -> Any:
        """Sample data."""
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            return data.sample(n=min(n, len(data)))
        elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
            import random
            data_list = list(data)
            return random.sample(data_list, min(n, len(data_list)))
        return data


class TransformationPipeline:
    """
    Data transformation pipeline.
    
    This class represents a sequence of transformation steps that can be
    applied to data in order. It provides methods for applying the pipeline
    and managing the transformation steps.
    """
    
    def __init__(self, steps: List[TransformationStep], config: Optional[ExportConfig] = None):
        """
        Initialize transformation pipeline.
        
        Args:
            steps: List of transformation steps
            config: Export configuration
        """
        self.steps = steps
        self.config = config or ExportConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def transform(self, data: Any) -> Any:
        """
        Apply the transformation pipeline to data.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        try:
            current_data = data
            
            for i, step in enumerate(self.steps):
                self.logger.debug(f"Applying step {i+1}/{len(self.steps)}: {step.get_name()}")
                
                try:
                    current_data = step.apply(current_data)
                except Exception as e:
                    self.logger.error(f"Step '{step.get_name()}' failed: {e}")
                    if self.config.strict_mode:
                        raise
                    else:
                        self.logger.warning(f"Skipping step '{step.get_name()}' due to error")
                        continue
            
            self.logger.info(f"Pipeline completed with {len(self.steps)} steps")
            return current_data
            
        except Exception as e:
            self.logger.error(f"Pipeline transformation failed: {e}")
            raise
    
    def add_step(self, name: str, func: Callable[[Any], Any]) -> 'TransformationPipeline':
        """
        Add a transformation step to the pipeline.
        
        Args:
            name: Step name
            func: Transformation function
            
        Returns:
            Updated pipeline
        """
        step = FunctionTransformationStep(name, func)
        self.steps.append(step)
        return self
    
    def remove_step(self, name: str) -> 'TransformationPipeline':
        """
        Remove a transformation step from the pipeline.
        
        Args:
            name: Step name to remove
            
        Returns:
            Updated pipeline
        """
        self.steps = [step for step in self.steps if step.get_name() != name]
        return self
    
    def get_steps(self) -> List[str]:
        """
        Get list of step names in the pipeline.
        
        Returns:
            List of step names
        """
        return [step.get_name() for step in self.steps]
    
    def get_step_count(self) -> int:
        """
        Get number of steps in the pipeline.
        
        Returns:
            Number of steps
        """
        return len(self.steps)
    
    def validate_pipeline(self) -> bool:
        """
        Validate the pipeline.
        
        Returns:
            True if pipeline is valid
        """
        try:
            for step in self.steps:
                if not callable(step.func):
                    return False
            return True
        except Exception:
            return False
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Get information about the pipeline.
        
        Returns:
            Dictionary with pipeline information
        """
        return {
            'step_count': len(self.steps),
            'steps': self.get_steps(),
            'valid': self.validate_pipeline()
        }
    
    def __len__(self) -> int:
        """Get number of steps in pipeline."""
        return len(self.steps)
    
    def __iter__(self) -> Iterator[TransformationStep]:
        """Iterate over pipeline steps."""
        return iter(self.steps)
    
    def __getitem__(self, index: int) -> TransformationStep:
        """Get step by index."""
        return self.steps[index]


class DataCleaner:
    """
    Specialized data cleaning utilities.
    
    This class provides common data cleaning operations that can be
    used in transformation pipelines or standalone.
    """
    
    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Initialize data cleaner.
        
        Args:
            config: Export configuration
        """
        self.config = config or ExportConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def clean_dataframe(self, df: 'pd.DataFrame') -> 'pd.DataFrame':
        """
        Clean a pandas DataFrame.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for DataFrame cleaning")
        
        try:
            cleaned_df = df.copy()
            
            # Remove duplicates
            cleaned_df = cleaned_df.drop_duplicates()
            
            # Remove empty rows
            cleaned_df = cleaned_df.dropna(how='all')
            
            # Remove empty columns
            cleaned_df = cleaned_df.dropna(axis=1, how='all')
            
            # Clean text columns
            text_cols = cleaned_df.select_dtypes(include=['object']).columns
            for col in text_cols:
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                cleaned_df[col] = cleaned_df[col].replace('', pd.NA)
            
            self.logger.info(f"Cleaned DataFrame: {df.shape} -> {cleaned_df.shape}")
            return cleaned_df
            
        except Exception as e:
            self.logger.error(f"DataFrame cleaning failed: {e}")
            raise
    
    def standardize_text(self, text: str) -> str:
        """
        Standardize text by removing extra whitespace and normalizing case.
        
        Args:
            text: Text to standardize
            
        Returns:
            Standardized text
        """
        if not isinstance(text, str):
            return str(text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize case (optional)
        # text = text.lower()
        
        return text
    
    def validate_data_quality(self, data: Any) -> Dict[str, Any]:
        """
        Validate data quality and return metrics.
        
        Args:
            data: Data to validate
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
                return {
                    'total_rows': len(data),
                    'total_columns': len(data.columns),
                    'missing_values': data.isnull().sum().sum(),
                    'duplicate_rows': data.duplicated().sum(),
                    'completeness': (1 - data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100,
                    'data_types': data.dtypes.to_dict()
                }
            else:
                return {
                    'total_items': len(data) if hasattr(data, '__len__') else 1,
                    'type': type(data).__name__
                }
                
        except Exception as e:
            self.logger.error(f"Data quality validation failed: {e}")
            return {'error': str(e)}







