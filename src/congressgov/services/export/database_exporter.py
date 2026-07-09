"""
Database export functionality using SQLAlchemy.

This module provides comprehensive database export capabilities,
including automatic schema generation, bulk inserts, and support
for multiple database backends.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Type
import logging

# Optional SQLAlchemy import with graceful fallback
try:
    from sqlalchemy import create_engine, Engine, Table, Column, MetaData, text
    from sqlalchemy.types import String, Integer, Float, DateTime, Boolean, Text, JSON
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.exc import SQLAlchemyError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    create_engine = None
    Engine = None
    Table = None
    Column = None
    MetaData = None
    text = None
    String = None
    Integer = None
    Float = None
    DateTime = None
    Boolean = None
    Text = None
    JSON = None
    UUID = None
    SQLAlchemyError = Exception

from .base import ExportConfig

logger = logging.getLogger(__name__)


class DatabaseExporter:
    """
    Database exporter using SQLAlchemy.
    
    This class provides comprehensive database export capabilities,
    including automatic schema generation from Pydantic models,
    bulk insert operations, and support for multiple database backends.
    
    Example:
        from sqlalchemy import create_engine
        from congressgov.services.export import DatabaseExporter
        
        engine = create_engine("postgresql://user:pass@localhost/congress")
        db_exporter = DatabaseExporter(engine)
        
        bills = bill_service.search(congress=118, limit=1000)
        db_exporter.export_to_db(bills, "bills_118th")
    """
    
    def __init__(self, engine: Optional[Engine] = None, config: Optional[ExportConfig] = None):
        """
        Initialize database exporter.
        
        Args:
            engine: SQLAlchemy engine (required for database operations)
            config: Export configuration (uses default if None)
        """
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError(
                "SQLAlchemy is required for database export. Install with: pip install sqlalchemy"
            )
        
        self.engine = engine
        self.config = config or ExportConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metadata = MetaData()
        
        if self.engine:
            self.metadata.bind = self.engine
    
    def export_to_db(self, data: Any, table_name: str, **kwargs) -> int:
        """
        Export data to database table.
        
        Args:
            data: Data to export
            table_name: Target table name
            **kwargs: Additional export options
                - if_exists: What to do if table exists ('fail', 'replace', 'append')
                - chunksize: Number of rows to insert at a time
                - index: Whether to include index column
                
        Returns:
            Number of records inserted
        """
        if not self.engine:
            raise ValueError("Database engine not configured")
        
        try:
            # Process data
            processed_data = self._process_data(data)
            
            if not processed_data:
                self.logger.warning("No data to export")
                return 0
            
            self.logger.info(f"Exporting {len(processed_data)} records to table '{table_name}'")
            
            # Create or get table
            table = self._get_or_create_table(table_name, processed_data[0])
            
            # Insert data
            records_inserted = self._insert_data(table, processed_data, **kwargs)
            
            self.logger.info(f"Successfully exported {records_inserted} records to '{table_name}'")
            return records_inserted
            
        except Exception as e:
            self.logger.error(f"Database export failed: {e}")
            raise
    
    def bulk_export(self, data_sources: List[tuple], **kwargs) -> Dict[str, int]:
        """
        Export multiple data sources to database.
        
        Args:
            data_sources: List of (data, table_name) tuples
            **kwargs: Additional export options
            
        Returns:
            Dictionary mapping table names to record counts
        """
        if not self.engine:
            raise ValueError("Database engine not configured")
        
        results = {}
        
        try:
            for data, table_name in data_sources:
                self.logger.info(f"Exporting to table '{table_name}'")
                records_inserted = self.export_to_db(data, table_name, **kwargs)
                results[table_name] = records_inserted
            
            self.logger.info(f"Bulk export completed: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Bulk export failed: {e}")
            raise
    
    def create_schema(self, model_class: Type, table_name: str) -> Table:
        """
        Create database schema from Pydantic model.
        
        Args:
            model_class: Pydantic model class
            table_name: Table name
            
        Returns:
            SQLAlchemy Table object
        """
        try:
            # Get model fields
            fields = model_class.model_fields
            
            # Create columns
            columns = []
            for field_name, field_info in fields.items():
                column = self._create_column(field_name, field_info)
                columns.append(column)
            
            # Create table
            table = Table(table_name, self.metadata, *columns)
            
            # Create table in database
            table.create(self.engine, checkfirst=True)
            
            self.logger.info(f"Created table '{table_name}' with {len(columns)} columns")
            return table
            
        except Exception as e:
            self.logger.error(f"Failed to create schema for '{table_name}': {e}")
            raise
    
    def _process_data(self, data: Any) -> List[Dict[str, Any]]:
        """Process data for database export."""
        try:
            # Handle single objects
            if hasattr(data, 'model_dump'):
                return [data.model_dump()]
            
            # Handle collections
            if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                processed = []
                for item in data:
                    if hasattr(item, 'model_dump'):
                        processed.append(item.model_dump())
                    elif isinstance(item, dict):
                        processed.append(item)
                    else:
                        processed.append(self._object_to_dict(item))
                return processed
            
            # Handle dictionaries
            if isinstance(data, dict):
                return [data]
            
            # Fallback: convert to dict
            return [self._object_to_dict(data)]
            
        except Exception as e:
            self.logger.error(f"Failed to process data: {e}")
            raise
    
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
    
    def _get_or_create_table(self, table_name: str, sample_record: Dict[str, Any]) -> Table:
        """Get existing table or create new one."""
        try:
            # Check if table exists
            if table_name in self.metadata.tables:
                return self.metadata.tables[table_name]
            
            # Create table from sample record
            columns = []
            for field_name, field_value in sample_record.items():
                column = self._infer_column_type(field_name, field_value)
                columns.append(column)
            
            table = Table(table_name, self.metadata, *columns)
            table.create(self.engine, checkfirst=True)
            
            return table
            
        except Exception as e:
            self.logger.error(f"Failed to get or create table '{table_name}': {e}")
            raise
    
    def _create_column(self, field_name: str, field_info: Any) -> Column:
        """Create SQLAlchemy column from Pydantic field info."""
        try:
            # Get field type
            field_type = field_info.annotation
            
            # Create column type
            column_type = self._get_column_type(field_type)
            
            # Create column
            return Column(field_name, column_type)
            
        except Exception as e:
            self.logger.warning(f"Failed to create column for '{field_name}': {e}")
            # Fallback to text column
            return Column(field_name, Text)
    
    def _infer_column_type(self, field_name: str, field_value: Any) -> Column:
        """Infer column type from field value."""
        try:
            if field_value is None:
                return Column(field_name, Text, nullable=True)
            
            if isinstance(field_value, bool):
                return Column(field_name, Boolean)
            elif isinstance(field_value, int):
                return Column(field_name, Integer)
            elif isinstance(field_value, float):
                return Column(field_name, Float)
            elif isinstance(field_value, str):
                # Check if it's a UUID
                if self._is_uuid(field_value):
                    return Column(field_name, String(36))
                # Check if it's a datetime string
                elif self._is_datetime_string(field_value):
                    return Column(field_name, String(50))  # Store as string to avoid datetime issues
                else:
                    # Use appropriate string length
                    max_length = min(len(field_value) * 2, 1000)  # Allow some growth
                    return Column(field_name, String(max_length))
            elif isinstance(field_value, (dict, list)):
                return Column(field_name, JSON)
            else:
                return Column(field_name, Text)
                
        except Exception as e:
            self.logger.warning(f"Failed to infer type for '{field_name}': {e}")
            return Column(field_name, Text)
    
    def _get_column_type(self, field_type: Any) -> Any:
        """Get SQLAlchemy column type from Python type."""
        try:
            # Handle Union types (like Optional[str])
            if hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
                # Get the non-None type
                args = field_type.__args__
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    field_type = non_none_types[0]
            
            # Map Python types to SQLAlchemy types
            if field_type == bool:
                return Boolean
            elif field_type == int:
                return Integer
            elif field_type == float:
                return Float
            elif field_type == str:
                return String(255)
            elif field_type == dict or field_type == list:
                return JSON
            else:
                return Text
                
        except Exception as e:
            self.logger.warning(f"Failed to map type {field_type}: {e}")
            return Text
    
    def _is_uuid(self, value: str) -> bool:
        """Check if a string is a UUID."""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, value, re.IGNORECASE))
    
    def _is_datetime_string(self, value: str) -> bool:
        """Check if a string is a datetime."""
        try:
            from datetime import datetime
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            return False
    
    def _insert_data(self, table: Table, data: List[Dict[str, Any]], **kwargs) -> int:
        """Insert data into table."""
        try:
            if_exists = kwargs.get('if_exists', 'append')
            chunksize = kwargs.get('chunksize', self.config.chunk_size)
            
            # Handle different if_exists options
            if if_exists == 'replace':
                # Drop and recreate table
                table.drop(self.engine, checkfirst=True)
                table.create(self.engine)
            elif if_exists == 'fail' and self.engine.has_table(table.name):
                raise ValueError(f"Table '{table.name}' already exists")
            
            # Insert data in chunks
            total_inserted = 0
            for i in range(0, len(data), chunksize):
                chunk = data[i:i + chunksize]
                
                # Insert chunk
                with self.engine.begin() as conn:
                    conn.execute(table.insert(), chunk)
                
                total_inserted += len(chunk)
                
                # Progress callback
                if self.config.progress_callback:
                    self.config.progress_callback(total_inserted, len(data))
            
            return total_inserted
            
        except Exception as e:
            self.logger.error(f"Failed to insert data: {e}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a database table.
        
        Args:
            table_name: Table name
            
        Returns:
            Dictionary with table information
        """
        try:
            if not self.engine:
                raise ValueError("Database engine not configured")
            
            # Check if table exists using inspect
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            
            if table_name not in inspector.get_table_names():
                return {'exists': False}
            
            # Get table metadata
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            
            info = {
                'exists': True,
                'columns': [col.name for col in table.columns],
                'column_count': len(table.columns),
                'column_types': {col.name: str(col.type) for col in table.columns}
            }
            
            # Get row count
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    info['row_count'] = result.scalar()
            except Exception:
                info['row_count'] = None
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get table info: {e}")
            return {'error': str(e)}
    
    def validate_connection(self) -> bool:
        """
        Validate database connection.
        
        Returns:
            True if connection is valid
        """
        try:
            if not self.engine:
                return False
            
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
            
        except Exception as e:
            self.logger.error(f"Database connection validation failed: {e}")
            return False
    
    def set_engine(self, engine: Engine) -> None:
        """
        Set database engine.
        
        Args:
            engine: SQLAlchemy engine
        """
        self.engine = engine
        self.metadata.bind = engine
    
    def get_engine(self) -> Optional[Engine]:
        """
        Get database engine.
        
        Returns:
            SQLAlchemy engine or None
        """
        return self.engine
