"""
Handles output generation and data visualization for the financial analysis.

This module provides functions for generating visualizations, saving results,
and formatting output data for the financial analysis results.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Union, Optional, List, Tuple
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import matplotlib.style as style
import seaborn as sns
import pandas as pd
from datetime import datetime
import numpy as np
from dataclasses import dataclass, asdict
import threading

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] %(message)s',
    handlers=[
        logging.FileHandler('analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PlotConfig:
    """Configuration for plot generation."""
    title: str
    xlabel: str
    ylabel: str
    figsize: Tuple[int, int] = (10, 6)
    style: str = 'default'
    dpi: int = 300
    format: str = 'png'

class OutputHandlerError(Exception):
    """Base exception for output handler errors."""
    pass

class FileOperationError(OutputHandlerError):
    """Exception for file operation errors."""
    pass

class PlottingError(OutputHandlerError):
    """Exception for plotting errors."""
    pass

class OutputHandler:
    """Handles output generation and data visualization."""
    
    def __init__(self, output_dir: Optional[str] = None, cache_size: int = 128):
        """
        Initialize the output handler.
        
        Args:
            output_dir: Directory to save outputs. Defaults to './outputs'
            cache_size: Size of the LRU cache for results
        """
        self.output_dir = Path(output_dir or './outputs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._plot_cache = {}
        
        # Set up thread pool for parallel processing
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Configure default plot settings
        style.use('default')
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'grid.alpha': 0.3,
            'savefig.dpi': 300,
            'figure.autolayout': True
        })
    
    @lru_cache(maxsize=128)
    def load_results(self, filepath: str) -> Dict[str, Any]:
        """
        Load and cache analysis results from JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Dict[str, Any]: Loaded results
            
        Raises:
            FileOperationError: If file cannot be read
        """
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise FileOperationError(f"Failed to load results from {filepath}: {str(e)}")
    
    def save_results(self, results: Dict[str, Any], filename: str) -> str:
        """
        Save analysis results to JSON file with atomic write.
        
        Args:
            results: Dictionary containing analysis results
            filename: Name for the output file
            
        Returns:
            str: Path to saved file
            
        Raises:
            FileOperationError: If unable to write to file
        """
        filepath = self.output_dir / f"{filename}_{datetime.now():%Y%m%d_%H%M%S}.json"
        temp_filepath = filepath.with_suffix('.tmp')
        
        try:
            # Write to temporary file first
            with open(temp_filepath, 'w') as f:
                json.dump(results, f, indent=4)
            
            # Atomic rename
            temp_filepath.rename(filepath)
            logger.info(f"Results saved to {filepath}")
            return str(filepath)
            
        except Exception as e:
            if temp_filepath.exists():
                temp_filepath.unlink()
            raise FileOperationError(f"Failed to save results: {str(e)}")
    
    def create_financial_dashboard(
        self,
        metrics: Dict[str, float],
        save_path: Optional[str] = None,
        config: Optional[PlotConfig] = None
    ) -> Optional[str]:
        """
        Create a dashboard visualization of financial metrics.
        
        Args:
            metrics: Dictionary of financial metrics
            save_path: Optional path to save the dashboard
            config: Optional plot configuration
            
        Returns:
            Optional[str]: Path to saved dashboard if save_path is provided
            
        Raises:
            PlottingError: If dashboard creation fails
        """
        if not metrics:
            raise ValueError("No metrics provided for dashboard")
            
        config = config or PlotConfig(
            title='Financial Analysis Dashboard',
            xlabel='Metric',
            ylabel='Value',
            figsize=(15, 10)
        )
        
        try:
            with self._lock:  # Thread safety for matplotlib
                fig, axes = plt.subplots(2, 2, figsize=config.figsize)
                fig.suptitle(config.title, fontsize=16)
                
                # Plot metrics in parallel
                plot_tasks = [
                    (axes[0, 0], 'ROI', metrics.get('roi', 0), '%'),
                    (axes[0, 1], 'Market Growth', metrics.get('market_growth', 0), '%'),
                    (axes[1, 0], 'Operating Margin', metrics.get('operating_margin', 0), '%'),
                    (axes[1, 1], 'Revenue Growth', metrics.get('revenue_growth', 0), '%')
                ]
                
                with ThreadPoolExecutor() as executor:
                    executor.map(lambda args: self._plot_metric(*args), plot_tasks)
                
                plt.tight_layout()
                
                if save_path:
                    plt.savefig(save_path, dpi=config.dpi, format=config.format)
                    logger.info(f"Dashboard saved to {save_path}")
                    plt.close()
                    return save_path
                else:
                    plt.show()
                    plt.close()
                    return None
                    
        except Exception as e:
            plt.close()
            raise PlottingError(f"Failed to create dashboard: {str(e)}")
    
    def _plot_metric(
        self,
        ax: plt.Axes,
        title: str,
        value: float,
        unit: str,
        color: str = 'skyblue'
    ) -> None:
        """
        Helper method to create individual metric plots.
        
        Args:
            ax: Matplotlib axes
            title: Plot title
            value: Metric value
            unit: Unit of measurement
            color: Bar color
        """
        ax.bar([''], [value], color=color)
        ax.set_title(f"{title}\n{value:.1f}{unit}")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, axis='y', alpha=0.3)
    
    def export_to_excel(
        self,
        data: Dict[str, Any],
        filename: str,
        sheet_configs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> str:
        """
        Export results to Excel file with multiple sheets and formatting.
        
        Args:
            data: Dictionary containing data for different sheets
            filename: Name for the Excel file
            sheet_configs: Optional configurations for each sheet
            
        Returns:
            str: Path to saved Excel file
            
        Raises:
            FileOperationError: If export fails
        """
        filepath = self.output_dir / f"{filename}_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, sheet_data in data.items():
                    df = pd.DataFrame(sheet_data)
                    
                    # Apply sheet-specific configurations
                    config = sheet_configs.get(sheet_name, {}) if sheet_configs else {}
                    
                    # Write data with configurations
                    df.to_excel(
                        writer,
                        sheet_name=sheet_name,
                        index=config.get('include_index', False),
                        float_format=config.get('float_format', '%.2f')
                    )
                    
                    # Get the worksheet
                    worksheet = writer.sheets[sheet_name]
                    
                    # Auto-adjust column widths
                    for idx, col in enumerate(df.columns):
                        max_length = max(
                            df[col].astype(str).apply(len).max(),
                            len(str(col))
                        )
                        worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
            
            logger.info(f"Excel file exported to {filepath}")
            return str(filepath)
            
        except Exception as e:
            raise FileOperationError(f"Failed to export to Excel: {str(e)}")
    
    def generate_summary_plots(
        self,
        data: Dict[str, Any],
        plot_type: str = 'line',
        save_dir: Optional[str] = None,
        config: Optional[PlotConfig] = None
    ) -> Dict[str, str]:
        """
        Generate summary plots for different metrics with parallel processing.
        
        Args:
            data: Dictionary containing time series data
            plot_type: Type of plot ('line', 'bar', or 'scatter')
            save_dir: Optional directory to save plots
            config: Optional plot configuration
            
        Returns:
            Dict[str, str]: Dictionary mapping metric names to plot file paths
            
        Raises:
            PlottingError: If plot generation fails
        """
        if not isinstance(data, dict) or not data:
            raise ValueError("Invalid or empty data provided")
        
        plot_paths = {}
        save_dir = Path(save_dir) if save_dir else self.output_dir
        
        try:
            # Process each metric in parallel
            def process_metric(metric_data: Tuple[str, List[float]]) -> Tuple[str, str]:
                metric, values = metric_data
                
                with self._lock:
                    plt.figure(figsize=config.figsize if config else (10, 6))
                    
                    if plot_type == 'line':
                        plt.plot(values, marker='o')
                    elif plot_type == 'bar':
                        plt.bar(range(len(values)), values)
                    elif plot_type == 'scatter':
                        plt.scatter(range(len(values)), values)
                    else:
                        raise ValueError(f"Unsupported plot type: {plot_type}")
                    
                    plt.title(f"{metric} Over Time")
                    plt.xlabel("Time Period")
                    plt.ylabel(metric)
                    
                    save_path = save_dir / f"{metric.lower().replace(' ', '_')}.png"
                    plt.savefig(save_path, dpi=300)
                    plt.close()
                    
                    return metric, str(save_path)
            
            # Use thread pool to process metrics in parallel
            with ThreadPoolExecutor() as executor:
                results = executor.map(process_metric, data.items())
                plot_paths = dict(results)
            
            return plot_paths
            
        except Exception as e:
            raise PlottingError(f"Failed to generate plots: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self._executor.shutdown(wait=True)
        plt.close('all')  # Clean up any remaining plots
        
        # Clear the cache if we're exiting
        self._plot_cache.clear()