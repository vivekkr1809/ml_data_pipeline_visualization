"""Contour plot renderer implementation using Matplotlib"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional
from src.core.interfaces.renderer import IRenderer, RenderConfig
from src.core.interfaces.analyzer import AnalysisResult


class ContourRenderer(IRenderer):
    """
    Renderer for contour plots using Matplotlib
    Supports filled contours and contour lines
    """

    def __init__(self):
        """Initialize contour renderer"""
        self._renderer_type = "contour"

    def render(self,
               data: pd.DataFrame,
               config: RenderConfig,
               analysis_result: Optional[AnalysisResult] = None,
               **kwargs) -> Figure:
        """
        Render contour plot

        Args:
            data: DataFrame with 3 columns (x, y, z)
            config: Rendering configuration
            analysis_result: Optional pre-computed analysis results with grid data
            **kwargs: Additional parameters
                - column_x: X column name
                - column_y: Y column name
                - column_z: Z column name
                - filled: Show filled contours (default: True)
                - show_points: Show original data points (default: True)
                - levels: Number of contour levels (default: 15)
                - colormap: Matplotlib colormap (default: 'viridis')

        Returns:
            Matplotlib Figure object

        Raises:
            ValueError: If data is invalid
        """
        if not self.validate_data(data, **kwargs):
            raise ValueError("Invalid data for contour plot")

        # Extract columns
        column_x = kwargs.get('column_x', data.columns[0])
        column_y = kwargs.get('column_y', data.columns[1])
        column_z = kwargs.get('column_z', data.columns[2])

        # Get parameters
        filled = kwargs.get('filled', True)
        show_points = kwargs.get('show_points', True)
        levels = kwargs.get('levels', 15)
        colormap = kwargs.get('colormap', 'viridis')

        # Create figure
        fig = Figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)

        # Apply style if specified
        if config.style:
            plt.style.use(config.style)

        # Get grid data from analysis result or use raw data
        if analysis_result and 'grid_x' in analysis_result.metadata:
            xi = analysis_result.metadata['grid_x']
            yi = analysis_result.metadata['grid_y']
            zi = analysis_result.metadata['grid_z']
            xi_grid, yi_grid = np.meshgrid(xi, yi)

            # Plot filled contours
            if filled:
                contourf = ax.contourf(xi_grid, yi_grid, zi, levels=levels,
                                      cmap=colormap, alpha=0.8)
                cbar = fig.colorbar(contourf, ax=ax, label=column_z)

            # Plot contour lines
            contour = ax.contour(xi_grid, yi_grid, zi, levels=levels,
                                colors='black', alpha=0.4, linewidths=0.5)
            ax.clabel(contour, inline=True, fontsize=8, fmt='%.1f')

            # Plot original data points if requested
            if show_points:
                x_orig = analysis_result.metadata['original_x']
                y_orig = analysis_result.metadata['original_y']
                ax.scatter(x_orig, y_orig, c='red', s=20, alpha=0.6,
                          edgecolors='white', linewidth=0.5, label='Data points',
                          zorder=5)

        else:
            # Fallback: plot scatter without interpolation
            clean_data = data[[column_x, column_y, column_z]].dropna()
            x = clean_data[column_x].values
            y = clean_data[column_y].values
            z = clean_data[column_z].values

            scatter = ax.scatter(x, y, c=z, cmap=colormap, s=50, alpha=0.8,
                                edgecolors='white', linewidth=0.5)
            fig.colorbar(scatter, ax=ax, label=column_z)

        # Set labels
        ax.set_xlabel(config.xlabel or column_x, fontsize=11, fontweight='bold')
        ax.set_ylabel(config.ylabel or column_y, fontsize=11, fontweight='bold')
        ax.set_title(config.title or f'Contour Plot: {column_z}',
                    fontsize=13, fontweight='bold', pad=15)

        # Add grid for better readability
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

        if show_points and analysis_result:
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
        Render contour plot with metrics annotation

        Args:
            data: DataFrame with 3 columns
            config: Rendering configuration
            analysis_result: Analysis results to display
            **kwargs: Additional parameters

        Returns:
            Figure with metrics annotation
        """
        # Render base plot
        fig = self.render(data, config, analysis_result, **kwargs)
        ax = fig.axes[0]

        # Get z column name
        column_z = kwargs.get('column_z', data.columns[2])

        # Create metrics text
        z_min = analysis_result.get_metric('z_min', 0)
        z_max = analysis_result.get_metric('z_max', 0)
        z_mean = analysis_result.get_metric('z_mean', 0)
        z_std = analysis_result.get_metric('z_std', 0)
        n_points = analysis_result.get_metric('n_points', 0)

        metrics_text = (
            f'{column_z} Statistics:\n'
            f'Min = {z_min:.2f}\n'
            f'Max = {z_max:.2f}\n'
            f'Mean = {z_mean:.2f}\n'
            f'Std = {z_std:.2f}\n'
            f'n = {n_points}'
        )

        # Add text box with metrics
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.85)
        ax.text(0.02, 0.98, metrics_text,
               transform=ax.transAxes,
               fontsize=9,
               verticalalignment='top',
               bbox=props,
               family='monospace')

        return fig

    def validate_data(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        Validate if data is suitable for contour plot

        Args:
            data: DataFrame to validate
            **kwargs: Optional column specifications

        Returns:
            True if data is valid
        """
        if data is None or data.empty:
            return False

        # Check specified columns
        column_x = kwargs.get('column_x', data.columns[0] if len(data.columns) > 0 else None)
        column_y = kwargs.get('column_y', data.columns[1] if len(data.columns) > 1 else None)
        column_z = kwargs.get('column_z', data.columns[2] if len(data.columns) > 2 else None)

        if column_x is None or column_y is None or column_z is None:
            return False

        if column_x not in data.columns or column_y not in data.columns or column_z not in data.columns:
            return False

        # Check if numeric
        if not pd.api.types.is_numeric_dtype(data[column_x]):
            return False
        if not pd.api.types.is_numeric_dtype(data[column_y]):
            return False
        if not pd.api.types.is_numeric_dtype(data[column_z]):
            return False

        # Need at least 3 data points
        clean_data = data[[column_x, column_y, column_z]].dropna()
        if len(clean_data) < 3:
            return False

        return True

    def get_renderer_type(self) -> str:
        """
        Get renderer type

        Returns:
            'contour'
        """
        return self._renderer_type
