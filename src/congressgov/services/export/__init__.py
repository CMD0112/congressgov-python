"""
Data export and integration for congressgov: multi-format file export
(CSV/Excel/JSON/Parquet), pandas DataFrame conversion, SQLAlchemy-backed
database export, transformation pipelines, and plotting helpers.

Usage:
    from congressgov.services.export import DataExporter, PandasIntegration
    from congressgov import Bill
    
    # Basic export
    bill_service = Bill(client=client)
    bills = bill_service.search(congress=118, limit=100)
    
    exporter = DataExporter()
    exporter.to_csv(bills, "bills.csv")
    exporter.to_excel(bills, "bills.xlsx")
    
    # Pandas integration
    pandas_int = PandasIntegration()
    df = pandas_int.to_dataframe(bills)
    df.to_parquet("bills.parquet")
"""

# Core export functionality
from .base import ExportConfig, ExportFormat, BaseExporter
from .exporters import CSVExporter, ExcelExporter, JSONExporter, ParquetExporter
from .data_exporter import DataExporter

# Pandas integration
from .pandas_integration import PandasIntegration

# Database export
from .database_exporter import DatabaseExporter

# Data transformation
from .transformer import DataTransformer, TransformationPipeline

# Visualization
from .visualization import VisualizationExporter

# Network graph projections
from . import graph as network_graph

__all__ = [
    # Core exports
    'ExportConfig',
    'ExportFormat', 
    'BaseExporter',
    'CSVExporter',
    'ExcelExporter',
    'JSONExporter',
    'ParquetExporter',
    'DataExporter',
    
    # Pandas integration
    'PandasIntegration',
    
    # Database export
    'DatabaseExporter',
    
    # Data transformation
    'DataTransformer',
    'TransformationPipeline',
    
    # Visualization
    'VisualizationExporter',

    # Network graph
    'network_graph',
]







