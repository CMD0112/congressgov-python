"""
Batch reporting and report generation.

This module provides the BatchReporter class for generating comprehensive
reports on batch processing operations in various formats.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
import json
import csv
import logging
from datetime import datetime
from pathlib import Path

from .base import BatchResult
from .analytics import BatchAnalytics

logger = logging.getLogger(__name__)


class BatchReporter:
    """
    Batch reporter for generating comprehensive reports.
    
    This class provides functionality to generate reports on batch processing
    operations in various formats including JSON, CSV, and HTML.
    
    Example:
        reporter = BatchReporter()
        
        # Generate JSON report
        await reporter.generate_json_report(result, "report.json")
        
        # Generate CSV report
        await reporter.generate_csv_report(result, "report.csv")
        
        # Generate HTML report
        await reporter.generate_html_report(result, "report.html")
    """
    
    def __init__(self, include_analytics: bool = True):
        """
        Initialize the batch reporter.
        
        Args:
            include_analytics: Whether to include analytics in reports
        """
        self.include_analytics = include_analytics
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def generate_json_report(
        self,
        result: BatchResult,
        filepath: Union[str, Path],
        analytics: Optional[BatchAnalytics] = None
    ) -> None:
        """
        Generate a JSON report.
        
        Args:
            result: Batch result to report on
            filepath: Path to save the report
            analytics: Optional analytics data to include
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        report_data = self._create_report_data(result, analytics)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"JSON report generated: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate JSON report: {e}")
            raise
    
    async def generate_csv_report(
        self,
        result: BatchResult,
        filepath: Union[str, Path],
        analytics: Optional[BatchAnalytics] = None
    ) -> None:
        """
        Generate a CSV report.
        
        Args:
            result: Batch result to report on
            filepath: Path to save the report
            analytics: Optional analytics data to include
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        self._create_report_data(result, analytics)
        
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write summary section
                writer.writerow(['Section', 'Metric', 'Value'])
                writer.writerow(['Summary', 'Total Items', result.total_items])
                writer.writerow(['Summary', 'Processed Items', result.processed_items])
                writer.writerow(['Summary', 'Successful Items', result.successful_items])
                writer.writerow(['Summary', 'Failed Items', result.failed_items])
                writer.writerow(['Summary', 'Retried Items', result.retried_items])
                writer.writerow(['Summary', 'Success Rate', f"{result.get_success_rate():.2f}%"])
                writer.writerow(['Summary', 'Progress', f"{result.get_progress():.2f}%"])
                
                if result.duration:
                    writer.writerow(['Summary', 'Duration (seconds)', result.duration.total_seconds()])
                    writer.writerow(['Summary', 'Items per Second', result.items_per_second])
                
                writer.writerow(['Summary', 'Memory Peak (MB)', result.memory_peak_mb])
                writer.writerow(['Summary', 'API Calls Made', result.api_calls_made])
                writer.writerow(['Summary', 'Status', result.status.value])
                
                # Write errors section
                if result.errors:
                    writer.writerow([])
                    writer.writerow(['Errors', 'Item', 'Error Type', 'Error Message'])
                    for item, error in result.errors:
                        writer.writerow(['Errors', str(item), type(error).__name__, str(error)])
                
                # Write analytics section
                if analytics and self.include_analytics:
                    analysis = analytics.analyze_performance()
                    if 'bottlenecks' in analysis:
                        writer.writerow([])
                        writer.writerow(['Bottlenecks', 'Type', 'Severity', 'Description', 'Recommendation'])
                        for bottleneck in analysis['bottlenecks']:
                            writer.writerow([
                                'Bottlenecks',
                                bottleneck['bottleneck_type'],
                                bottleneck['severity'],
                                bottleneck['description'],
                                bottleneck['recommendation']
                            ])
            
            self.logger.info(f"CSV report generated: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate CSV report: {e}")
            raise
    
    async def generate_html_report(
        self,
        result: BatchResult,
        filepath: Union[str, Path],
        analytics: Optional[BatchAnalytics] = None,
        title: str = "Batch Processing Report"
    ) -> None:
        """
        Generate an HTML report.
        
        Args:
            result: Batch result to report on
            filepath: Path to save the report
            analytics: Optional analytics data to include
            title: Title for the report
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        self._create_report_data(result, analytics)
        
        try:
            html_content = self._generate_html_content(result, analytics, title)
            
            with open(filepath, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}")
            raise
    
    def _create_report_data(
        self,
        result: BatchResult,
        analytics: Optional[BatchAnalytics] = None
    ) -> Dict[str, Any]:
        """Create report data structure."""
        data = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0',
                'generator': 'BatchReporter'
            },
            'batch_result': result.to_dict()
        }
        
        if analytics and self.include_analytics:
            data['analytics'] = analytics.get_performance_summary()
        
        return data
    
    def _generate_html_content(
        self,
        result: BatchResult,
        analytics: Optional[BatchAnalytics] = None,
        title: str = "Batch Processing Report"
    ) -> str:
        """Generate HTML content for the report."""
        # Calculate additional metrics
        success_rate = result.get_success_rate()
        progress = result.get_progress()
        remaining_time = result.get_remaining_time()
        
        # Status color
        status_color = {
            'completed': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#ffc107',
            'running': '#007bff',
            'pending': '#6c757d'
        }.get(result.status.value, '#6c757d')
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #495057;
            margin-bottom: 5px;
        }}
        .metric-label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            background-color: {status_color};
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            width: {progress}%;
            transition: width 0.3s ease;
        }}
        .error-list {{
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #e9ecef;
            border-radius: 4px;
        }}
        .error-item {{
            padding: 10px 15px;
            border-bottom: 1px solid #e9ecef;
            font-family: monospace;
            font-size: 0.9em;
        }}
        .error-item:last-child {{
            border-bottom: none;
        }}
        .bottleneck {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 10px;
        }}
        .bottleneck.high {{
            background: #f8d7da;
            border-color: #f5c6cb;
        }}
        .bottleneck.critical {{
            background: #f8d7da;
            border-color: #f5c6cb;
            border-left: 4px solid #dc3545;
        }}
        .recommendation {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 10px;
        }}
        .recommendation.high {{
            background: #d4edda;
            border-color: #c3e6cb;
        }}
        .recommendation.critical {{
            background: #f8d7da;
            border-color: #f5c6cb;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>Summary</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{result.total_items:,}</div>
                        <div class="metric-label">Total Items</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{result.processed_items:,}</div>
                        <div class="metric-label">Processed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{result.successful_items:,}</div>
                        <div class="metric-label">Successful</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{result.failed_items:,}</div>
                        <div class="metric-label">Failed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{success_rate:.1f}%</div>
                        <div class="metric-label">Success Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">
                            <span class="status-badge">{result.status.value.title()}</span>
                        </div>
                        <div class="metric-label">Status</div>
                    </div>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <p style="text-align: center; margin-top: 10px;">
                    Progress: {progress:.1f}% ({result.processed_items:,} of {result.total_items:,} items)
                </p>
            </div>
            
            <div class="section">
                <h2>Performance Metrics</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{result.items_per_second:.1f}</div>
                        <div class="metric-label">Items per Second</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{result.memory_peak_mb:.1f} MB</div>
                        <div class="metric-label">Peak Memory</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{result.api_calls_made:,}</div>
                        <div class="metric-label">API Calls</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{result.retried_items:,}</div>
                        <div class="metric-label">Retried Items</div>
                    </div>
                </div>
                
                {f'''
                <p><strong>Duration:</strong> {result.duration.total_seconds():.2f} seconds</p>
                <p><strong>Start Time:</strong> {result.start_time.strftime('%Y-%m-%d %H:%M:%S') if result.start_time else 'N/A'}</p>
                <p><strong>End Time:</strong> {result.end_time.strftime('%Y-%m-%d %H:%M:%S') if result.end_time else 'N/A'}</p>
                ''' if result.duration else ''}
                
                {f'<p><strong>Estimated Remaining Time:</strong> {remaining_time.total_seconds():.0f} seconds</p>' if remaining_time else ''}
            </div>
        """
        
        # Add errors section
        if result.errors:
            html += f"""
            <div class="section">
                <h2>Errors ({len(result.errors)})</h2>
                <div class="error-list">
            """
            for item, error in result.errors[:50]:  # Limit to first 50 errors
                html += f"""
                    <div class="error-item">
                        <strong>Item:</strong> {str(item)[:100]}{'...' if len(str(item)) > 100 else ''}<br>
                        <strong>Error:</strong> {type(error).__name__}: {str(error)[:200]}{'...' if len(str(error)) > 200 else ''}
                    </div>
                """
            html += """
                </div>
            </div>
            """
        
        # Add analytics section
        if analytics and self.include_analytics:
            analysis = analytics.analyze_performance()
            
            if 'bottlenecks' in analysis and analysis['bottlenecks']:
                html += """
                <div class="section">
                    <h2>Performance Bottlenecks</h2>
                """
                for bottleneck in analysis['bottlenecks']:
                    severity_class = bottleneck['severity']
                    html += f"""
                    <div class="bottleneck {severity_class}">
                        <h4>{bottleneck['bottleneck_type'].replace('_', ' ').title()}</h4>
                        <p><strong>Severity:</strong> {bottleneck['severity'].title()}</p>
                        <p><strong>Description:</strong> {bottleneck['description']}</p>
                        <p><strong>Recommendation:</strong> {bottleneck['recommendation']}</p>
                    </div>
                    """
                html += "</div>"
            
            # Add optimization recommendations
            recommendations = analytics.get_optimization_recommendations()
            if recommendations:
                html += """
                <div class="section">
                    <h2>Optimization Recommendations</h2>
                """
                for rec in recommendations:
                    priority_class = rec.priority
                    html += f"""
                    <div class="recommendation {priority_class}">
                        <h4>{rec.title}</h4>
                        <p><strong>Priority:</strong> {rec.priority.title()}</p>
                        <p><strong>Description:</strong> {rec.description}</p>
                        <p><strong>Expected Improvement:</strong> {rec.expected_improvement}</p>
                        <p><strong>Implementation Effort:</strong> {rec.implementation_effort}</p>
                    </div>
                    """
                html += "</div>"
        
        html += """
        </div>
        
        <div class="footer">
            <p>Report generated by BatchReporter v1.0</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    async def generate_summary_report(
        self,
        results: List[BatchResult],
        filepath: Union[str, Path],
        title: str = "Batch Processing Summary Report"
    ) -> None:
        """
        Generate a summary report for multiple batch results.
        
        Args:
            results: List of batch results to summarize
            filepath: Path to save the report
            title: Title for the report
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate summary statistics
        total_items = sum(r.total_items for r in results)
        total_processed = sum(r.processed_items for r in results)
        total_successful = sum(r.successful_items for r in results)
        total_failed = sum(r.failed_items for r in results)
        total_retried = sum(r.retried_items for r in results)
        
        overall_success_rate = (total_successful / total_processed * 100) if total_processed > 0 else 0
        
        # Create summary data
        summary_data = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0',
                'generator': 'BatchReporter',
                'report_type': 'summary'
            },
            'summary': {
                'total_batches': len(results),
                'total_items': total_items,
                'total_processed': total_processed,
                'total_successful': total_successful,
                'total_failed': total_failed,
                'total_retried': total_retried,
                'overall_success_rate': overall_success_rate
            },
            'individual_results': [r.to_dict() for r in results]
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(summary_data, f, indent=2, default=str)
            
            self.logger.info(f"Summary report generated: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary report: {e}")
            raise







