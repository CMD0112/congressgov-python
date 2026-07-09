"""
Visualization utilities for data export and analysis.

This module provides comprehensive visualization capabilities for
congressgov data, including common chart types and
custom visualization support.
"""

from __future__ import annotations

from typing import Any, List, Optional, Union
import logging
from pathlib import Path

# Optional visualization imports with graceful fallback
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    mdates = None
    Figure = None

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    sns = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from .base import ExportConfig

logger = logging.getLogger(__name__)


class VisualizationExporter:
    """
    Visualization exporter for congressgov.
    
    This class provides comprehensive visualization capabilities for
    congressional data, including common chart types, custom plots,
    and export functionality.
    
    Example:
        viz_exporter = VisualizationExporter()
        bills = bill_service.search(congress=118, limit=1000)
        
        # Create bill type distribution chart
        viz_exporter.plot_bill_types(bills, "bill_types.png")
        
        # Create timeline chart
        viz_exporter.plot_timeline(bills, "bill_timeline.png")
    """
    
    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Initialize visualization exporter.
        
        Args:
            config: Export configuration (uses default if None)
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError(
                "matplotlib is required for visualization. Install with: pip install matplotlib"
            )
        
        self.config = config or ExportConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Set up matplotlib style
        if SEABORN_AVAILABLE:
            sns.set_style("whitegrid")
            sns.set_palette("husl")
        
        # Configure matplotlib
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
    
    def plot_bill_types(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Create bill type distribution chart.
        
        Args:
            data: Bill data to visualize
            filepath: Output file path
            **kwargs: Additional plot options
        """
        try:
            df = self._prepare_dataframe(data)
            
            type_col = self._find_type_column(df)
            if type_col is None:
                raise ValueError(
                    "Data must contain a bill type column (e.g. 'type', 'billType') "
                    "for bill type visualization"
                )
            
            # Create figure
            fig, ax = plt.subplots(figsize=kwargs.get('figsize', (12, 8)))
            
            # Count bill types
            type_counts = df[type_col].value_counts()
            
            # Create bar chart
            type_counts.plot(kind='bar', ax=ax, color=kwargs.get('color', 'skyblue'))
            
            # Customize chart
            ax.set_title(kwargs.get('title', 'Bill Types Distribution'), fontsize=16, fontweight='bold')
            ax.set_xlabel('Bill Type', fontsize=12)
            ax.set_ylabel('Number of Bills', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            if kwargs.get('show_values', True):
                for i, v in enumerate(type_counts.values):
                    ax.text(i, v + 0.5, str(v), ha='center', va='bottom')
            
            # Adjust layout and save
            plt.tight_layout()
            self._save_plot(fig, filepath, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Failed to create bill types plot: {e}")
            raise
    
    def plot_timeline(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Create timeline chart of bill introductions.
        
        Args:
            data: Bill data to visualize
            filepath: Output file path
            **kwargs: Additional plot options
        """
        try:
            df = self._prepare_dataframe(data)
            
            # Find date column
            date_col = self._find_date_column(df)
            if not date_col:
                raise ValueError("Data must contain a date column for timeline visualization")
            
            # Convert to datetime
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col])
            
            # Create figure
            fig, ax = plt.subplots(figsize=kwargs.get('figsize', (14, 8)))
            
            # Group by date and count
            timeline_data = df.groupby(df[date_col].dt.date).size()
            
            # Create line plot
            timeline_data.plot(kind='line', ax=ax, marker='o', linewidth=2, markersize=4)
            
            # Customize chart
            ax.set_title(kwargs.get('title', 'Bills Introduced Over Time'), fontsize=16, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Number of Bills', fontsize=12)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            plt.xticks(rotation=45)
            
            # Add grid
            ax.grid(True, alpha=0.3)
            
            # Adjust layout and save
            plt.tight_layout()
            self._save_plot(fig, filepath, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Failed to create timeline plot: {e}")
            raise
    
    def plot_committee_activity(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Create committee activity heatmap.
        
        Args:
            data: Committee or bill data to visualize
            filepath: Output file path
            **kwargs: Additional plot options
        """
        try:
            df = self._prepare_dataframe(data)
            
            # Find committee and date columns
            committee_col = self._find_committee_column(df)
            date_col = self._find_date_column(df)
            
            if not committee_col or not date_col:
                raise ValueError("Data must contain committee and date columns for activity heatmap")
            
            # Convert to datetime
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col])
            
            # Create pivot table
            df['month'] = df[date_col].dt.to_period('M')
            pivot_data = df.groupby([committee_col, 'month']).size().unstack(fill_value=0)
            
            # Create figure
            fig, ax = plt.subplots(figsize=kwargs.get('figsize', (16, 10)))
            
            # Create heatmap
            if SEABORN_AVAILABLE:
                sns.heatmap(pivot_data, annot=True, fmt='d', cmap='YlOrRd', ax=ax)
            else:
                im = ax.imshow(pivot_data.values, cmap='YlOrRd', aspect='auto')
                plt.colorbar(im, ax=ax)
            
            # Customize chart
            ax.set_title(kwargs.get('title', 'Committee Activity Heatmap'), fontsize=16, fontweight='bold')
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Committee', fontsize=12)
            
            # Rotate x-axis labels
            plt.xticks(rotation=45)
            
            # Adjust layout and save
            plt.tight_layout()
            self._save_plot(fig, filepath, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Failed to create committee activity heatmap: {e}")
            raise
    
    def plot_member_activity(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Create member activity scatter plot.
        
        Args:
            data: Member or bill data to visualize
            filepath: Output file path
            **kwargs: Additional plot options
        """
        try:
            df = self._prepare_dataframe(data)
            
            # Find member and activity columns
            member_col = self._find_member_column(df)
            self._find_activity_column(df)
            
            if not member_col:
                raise ValueError("Data must contain a member column for member activity visualization")
            
            # Create figure
            fig, ax = plt.subplots(figsize=kwargs.get('figsize', (14, 8)))
            
            # Count activity by member
            member_activity = df[member_col].value_counts().head(kwargs.get('top_n', 20))
            
            # Create bar chart
            member_activity.plot(kind='bar', ax=ax, color=kwargs.get('color', 'lightcoral'))
            
            # Customize chart
            ax.set_title(kwargs.get('title', 'Top Members by Activity'), fontsize=16, fontweight='bold')
            ax.set_xlabel('Member', fontsize=12)
            ax.set_ylabel('Activity Count', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels
            if kwargs.get('show_values', True):
                for i, v in enumerate(member_activity.values):
                    ax.text(i, v + 0.5, str(v), ha='center', va='bottom')
            
            # Adjust layout and save
            plt.tight_layout()
            self._save_plot(fig, filepath, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Failed to create member activity plot: {e}")
            raise
    
    def plot_custom(self, data: Any, filepath: Union[str, Path], plot_func: callable, **kwargs) -> None:
        """
        Create custom plot using provided function.
        
        Args:
            data: Data to visualize
            filepath: Output file path
            plot_func: Function that creates the plot (receives data and ax)
            **kwargs: Additional plot options
        """
        try:
            df = self._prepare_dataframe(data)
            
            # Create figure
            fig, ax = plt.subplots(figsize=kwargs.get('figsize', (12, 8)))
            
            # Call custom plot function
            plot_func(df, ax, **kwargs)
            
            # Adjust layout and save
            plt.tight_layout()
            self._save_plot(fig, filepath, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Failed to create custom plot: {e}")
            raise
    
    def create_dashboard(self, data: Any, filepath: Union[str, Path], **kwargs) -> None:
        """
        Create a comprehensive dashboard with multiple charts.
        
        Args:
            data: Data to visualize
            filepath: Output file path
            **kwargs: Additional plot options
        """
        try:
            df = self._prepare_dataframe(data)
            
            # Create subplots
            fig, axes = plt.subplots(2, 2, figsize=kwargs.get('figsize', (16, 12)))
            fig.suptitle(kwargs.get('title', 'Congress.gov Dashboard'), fontsize=20, fontweight='bold')
            
            # Chart 1: Bill types distribution
            type_col = self._find_type_column(df)
            if type_col:
                type_counts = df[type_col].value_counts()
                type_counts.plot(kind='bar', ax=axes[0, 0], color='skyblue')
                axes[0, 0].set_title('Bill Types Distribution')
                axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Chart 2: Timeline
            date_col = self._find_date_column(df)
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                df_clean = df.dropna(subset=[date_col])
                timeline_data = df_clean.groupby(df_clean[date_col].dt.date).size()
                timeline_data.plot(kind='line', ax=axes[0, 1], marker='o')
                axes[0, 1].set_title('Bills Over Time')
                axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Chart 3: Member activity
            member_col = self._find_member_column(df)
            if member_col:
                member_activity = df[member_col].value_counts().head(10)
                member_activity.plot(kind='bar', ax=axes[1, 0], color='lightcoral')
                axes[1, 0].set_title('Top Members by Activity')
                axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Chart 4: Data summary
            axes[1, 1].text(0.5, 0.5, f'Total Records: {len(df)}\nColumns: {len(df.columns)}', 
                           ha='center', va='center', fontsize=14, 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            axes[1, 1].set_title('Data Summary')
            axes[1, 1].axis('off')
            
            # Adjust layout and save
            plt.tight_layout()
            self._save_plot(fig, filepath, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Failed to create dashboard: {e}")
            raise
    
    def _prepare_dataframe(self, data: Any) -> 'pd.DataFrame':
        """Prepare data as pandas DataFrame."""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for visualization")
        
        if isinstance(data, pd.DataFrame):
            return data
        
        # Convert to DataFrame
        from .pandas_integration import PandasIntegration
        pandas_int = PandasIntegration(self.config)
        return pandas_int.to_dataframe(data)
    
    def _find_type_column(self, df: 'pd.DataFrame') -> Optional[str]:
        """Find bill type column in DataFrame."""
        if 'type' in df.columns:
            return 'type'
        for col in df.columns:
            if col.lower() in ('billtype', 'bill_type'):
                return col
        type_cols = [col for col in df.columns if 'type' in col.lower()]
        return type_cols[0] if type_cols else None

    def _find_date_column(self, df: 'pd.DataFrame') -> Optional[str]:
        """Find date column in DataFrame."""
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        return date_cols[0] if date_cols else None
    
    def _find_committee_column(self, df: 'pd.DataFrame') -> Optional[str]:
        """Find committee column in DataFrame."""
        committee_cols = [col for col in df.columns if 'committee' in col.lower()]
        return committee_cols[0] if committee_cols else None
    
    def _find_member_column(self, df: 'pd.DataFrame') -> Optional[str]:
        """Find member column in DataFrame."""
        member_cols = [col for col in df.columns if 'member' in col.lower() or 'sponsor' in col.lower()]
        return member_cols[0] if member_cols else None
    
    def _find_activity_column(self, df: 'pd.DataFrame') -> Optional[str]:
        """Find activity column in DataFrame."""
        activity_cols = [col for col in df.columns if 'activity' in col.lower() or 'action' in col.lower()]
        return activity_cols[0] if activity_cols else None
    
    def _save_plot(self, fig: 'Figure', filepath: Union[str, Path], **kwargs) -> None:
        """Save plot to file."""
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Get save options
            dpi = kwargs.get('dpi', 300)
            bbox_inches = kwargs.get('bbox_inches', 'tight')
            format = kwargs.get('format', filepath.suffix[1:])
            
            # Save plot
            fig.savefig(filepath, dpi=dpi, bbox_inches=bbox_inches, format=format)
            
            # Close figure to free memory
            plt.close(fig)
            
            self.logger.info(f"Plot saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save plot: {e}")
            raise
    
    def get_available_plots(self) -> List[str]:
        """
        Get list of available plot types.
        
        Returns:
            List of available plot types
        """
        return [
            'bill_types',
            'timeline',
            'committee_activity',
            'member_activity',
            'custom',
            'dashboard'
        ]
    
    def set_style(self, style: str = 'whitegrid') -> None:
        """
        Set matplotlib/seaborn style.
        
        Args:
            style: Style name
        """
        if SEABORN_AVAILABLE:
            sns.set_style(style)
        else:
            plt.style.use(style)
    
    def set_palette(self, palette: str = 'husl') -> None:
        """
        Set color palette.
        
        Args:
            palette: Palette name
        """
        if SEABORN_AVAILABLE:
            sns.set_palette(palette)







