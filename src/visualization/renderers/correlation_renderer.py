"""Correlation plot renderer implementation"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional
from src.core.interfaces.renderer import IRenderer, RenderConfig
from src.core.interfaces.analyzer import AnalysisResult


class CorrelationRenderer(IRenderer):
    """
    Renderer for correlation plots with regression line
    Optimized for interactivity and low latency
    """

    def __init__(self):
        """Initialize correlation renderer"""
        self._renderer_type = "correlation"

    def render(self,
               data: pd.DataFrame,
               config: RenderConfig,
               analysis_result: Optional[AnalysisResult] = None,
               **kwargs) -> Figure:
        """
        Render correlation plot

        Args:
            data: DataFrame with 2 columns (x, y)
            config: Rendering configuration
            analysis_result: Optional pre-computed analysis results
            **kwargs: Additional parameters
                - column_x: X column name
                - column_y: Y column name
                - show_regression: Show regression line (default: True)
                - point_size: Scatter point size (default: 30)
                - point_alpha: Point transparency (default: 0.6)

        Returns:
            Matplotlib Figure object

        Raises:
            ValueError: If data is invalid
        """
        if not self.validate_data(data, **kwargs):
            raise ValueError("Invalid data for correlation plot")

        # Extract columns
        column_x = kwargs.get('column_x', data.columns[0])
        column_y = kwargs.get('column_y', data.columns[1])

        # Get clean data
        clean_data = data[[column_x, column_y]].dropna()
        x = clean_data[column_x].values
        y = clean_data[column_y].values

        # Create figure with optimized settings for performance
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)

        # Apply style if specified
        if config.style:
            plt.style.use(config.style)

        # Plot scatter points
        point_size = kwargs.get('point_size', 30)
        point_alpha = kwargs.get('point_alpha', 0.6)
        ax.scatter(x, y, alpha=point_alpha, s=point_size,
                  color='#2E86AB', edgecolors='white', linewidth=0.5,
                  label='Data points')

        # Add regression line if requested and analysis results available
        show_regression = kwargs.get('show_regression', True)
        if show_regression and analysis_result:
            slope = analysis_result.get_metric('slope')
            intercept = analysis_result.get_metric('intercept')

            if slope is not None and intercept is not None:
                # Create regression line
                x_line = np.array([x.min(), x.max()])
                y_line = slope * x_line + intercept
                ax.plot(x_line, y_line, 'r-', linewidth=2,
                       label=f'y = {slope:.3f}x + {intercept:.3f}')

        # Set labels
        ax.set_xlabel(config.xlabel or column_x, fontsize=11, fontweight='bold')
        ax.set_ylabel(config.ylabel or column_y, fontsize=11, fontweight='bold')
        ax.set_title(config.title or f'Correlation: {column_x} vs {column_y}',
                    fontsize=13, fontweight='bold', pad=15)

        # Add grid for better readability
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

        # Add legend
        ax.legend(loc='best', framealpha=0.9)

        # Tight layout for better appearance
        fig.tight_layout()

        return fig

    def render_with_metrics(self,
                           data: pd.DataFrame,
                           config: RenderConfig,
                           analysis_result: AnalysisResult,
                           **kwargs) -> Figure:
        """
        Render correlation plot with metrics annotation

        Args:
            data: DataFrame with 2 columns
            config: Rendering configuration
            analysis_result: Analysis results to display
            **kwargs: Additional parameters

        Returns:
            Figure with metrics annotation
        """
        # Render base plot
        fig = self.render(data, config, analysis_result, **kwargs)
        ax = fig.axes[0]

        # Create metrics text
        r2 = analysis_result.get_metric('r2', 0)
        rmse = analysis_result.get_metric('rmse', 0)
        slope = analysis_result.get_metric('slope', 0)
        n_points = analysis_result.get_metric('n_points', 0)

        metrics_text = (
            f'R² = {r2:.4f}\n'
            f'RMSE = {rmse:.4f}\n'
            f'Slope = {slope:.4f}\n'
            f'n = {n_points}'
        )

        # Add text box with metrics
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.05, 0.95, metrics_text,
               transform=ax.transAxes,
               fontsize=10,
               verticalalignment='top',
               bbox=props,
               family='monospace')

        return fig

    def validate_data(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        Validate if data is suitable for correlation plot

        Args:
            data: DataFrame to validate
            **kwargs: Optional column specifications

        Returns:
            True if data is valid
        """
        if data is None or data.empty:
            return False

        # Need at least 2 columns
        if len(data.columns) < 2:
            return False

        # Check specified columns
        column_x = kwargs.get('column_x', data.columns[0])
        column_y = kwargs.get('column_y', data.columns[1])

        if column_x not in data.columns or column_y not in data.columns:
            return False

        # Check if numeric
        if not pd.api.types.is_numeric_dtype(data[column_x]):
            return False
        if not pd.api.types.is_numeric_dtype(data[column_y]):
            return False

        # Need at least 1 data point
        clean_data = data[[column_x, column_y]].dropna()
        if len(clean_data) < 1:
            return False

        return True

    def get_renderer_type(self) -> str:
        """
        Get renderer type

        Returns:
            'correlation'
        """
        return self._renderer_type
