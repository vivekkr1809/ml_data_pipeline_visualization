"""Interactive contour plot renderer using Plotly"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Optional
from src.core.interfaces.renderer import RenderConfig
from src.core.interfaces.analyzer import AnalysisResult


class PlotlyContourRenderer:
    """
    Interactive renderer for contour plots using Plotly
    Supports 3D visualization and interactive exploration
    """

    def __init__(self):
        """Initialize Plotly contour renderer"""
        self._renderer_type = "plotly_contour"

    def render(self,
               data: pd.DataFrame,
               config: RenderConfig,
               analysis_result: Optional[AnalysisResult] = None,
               **kwargs) -> go.Figure:
        """
        Render interactive contour plot

        Args:
            data: DataFrame with 3 columns (x, y, z)
            config: Rendering configuration
            analysis_result: Optional pre-computed analysis results with grid data
            **kwargs: Additional parameters
                - column_x: X column name
                - column_y: Y column name
                - column_z: Z column name
                - show_points: Show original data points (default: True)
                - colorscale: Plotly colorscale (default: 'Viridis')
                - plot_3d: Show 3D surface plot (default: False)

        Returns:
            Plotly Figure object

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
        show_points = kwargs.get('show_points', True)
        colorscale = kwargs.get('colorscale', 'Viridis')
        plot_3d = kwargs.get('plot_3d', False)

        # Create figure
        if plot_3d:
            fig = self._render_3d(data, config, analysis_result, column_x, column_y, column_z,
                                 show_points, colorscale)
        else:
            fig = self._render_2d(data, config, analysis_result, column_x, column_y, column_z,
                                 show_points, colorscale)

        return fig

    def _render_2d(self, data, config, analysis_result, column_x, column_y, column_z,
                   show_points, colorscale):
        """Render 2D contour plot"""
        fig = go.Figure()

        # Get grid data from analysis result
        if analysis_result and 'grid_x' in analysis_result.metadata:
            xi = analysis_result.metadata['grid_x']
            yi = analysis_result.metadata['grid_y']
            zi = analysis_result.metadata['grid_z']

            # Add filled contour
            fig.add_trace(go.Contour(
                x=xi,
                y=yi,
                z=zi,
                colorscale=colorscale,
                name=column_z,
                contours=dict(
                    coloring='heatmap',
                    showlabels=True,
                    labelfont=dict(size=10, color='white')
                ),
                colorbar=dict(title=column_z),
                hovertemplate=f'{column_x}: %{{x:.2f}}<br>{column_y}: %{{y:.2f}}<br>{column_z}: %{{z:.2f}}<extra></extra>'
            ))

            # Add original data points if requested
            if show_points:
                x_orig = analysis_result.metadata['original_x']
                y_orig = analysis_result.metadata['original_y']
                z_orig = analysis_result.metadata['original_z']

                fig.add_trace(go.Scatter(
                    x=x_orig,
                    y=y_orig,
                    mode='markers',
                    name='Data points',
                    marker=dict(
                        size=6,
                        color=z_orig,
                        colorscale=colorscale,
                        line=dict(color='white', width=1),
                        showscale=False
                    ),
                    hovertemplate=f'{column_x}: %{{x:.2f}}<br>{column_y}: %{{y:.2f}}<br>{column_z}: %{{customdata:.2f}}<extra></extra>',
                    customdata=z_orig
                ))
        else:
            # Fallback: plot scatter without interpolation
            clean_data = data[[column_x, column_y, column_z]].dropna()
            x = clean_data[column_x].values
            y = clean_data[column_y].values
            z = clean_data[column_z].values

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='markers',
                name='Data points',
                marker=dict(
                    size=10,
                    color=z,
                    colorscale=colorscale,
                    showscale=True,
                    colorbar=dict(title=column_z),
                    line=dict(color='white', width=1)
                ),
                hovertemplate=f'{column_x}: %{{x:.2f}}<br>{column_y}: %{{y:.2f}}<br>{column_z}: %{{marker.color:.2f}}<extra></extra>'
            ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=config.title or f'Contour Plot: {column_z}',
                font=dict(size=16, family='Arial, sans-serif')
            ),
            xaxis_title=config.xlabel or column_x,
            yaxis_title=config.ylabel or column_y,
            hovermode='closest',
            template='plotly_white',
            showlegend=True,
            width=900,
            height=700,
            margin=dict(l=80, r=120, t=100, b=80)
        )

        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

        return fig

    def _render_3d(self, data, config, analysis_result, column_x, column_y, column_z,
                   show_points, colorscale):
        """Render 3D surface plot"""
        fig = go.Figure()

        # Get grid data from analysis result
        if analysis_result and 'grid_x' in analysis_result.metadata:
            xi = analysis_result.metadata['grid_x']
            yi = analysis_result.metadata['grid_y']
            zi = analysis_result.metadata['grid_z']

            # Add 3D surface
            fig.add_trace(go.Surface(
                x=xi,
                y=yi,
                z=zi,
                colorscale=colorscale,
                name=column_z,
                colorbar=dict(title=column_z),
                hovertemplate=f'{column_x}: %{{x:.2f}}<br>{column_y}: %{{y:.2f}}<br>{column_z}: %{{z:.2f}}<extra></extra>'
            ))

            # Add original data points if requested
            if show_points:
                x_orig = analysis_result.metadata['original_x']
                y_orig = analysis_result.metadata['original_y']
                z_orig = analysis_result.metadata['original_z']

                fig.add_trace(go.Scatter3d(
                    x=x_orig,
                    y=y_orig,
                    z=z_orig,
                    mode='markers',
                    name='Data points',
                    marker=dict(
                        size=4,
                        color='red',
                        line=dict(color='white', width=1)
                    ),
                    hovertemplate=f'{column_x}: %{{x:.2f}}<br>{column_y}: %{{y:.2f}}<br>{column_z}: %{{z:.2f}}<extra></extra>'
                ))

        # Update layout for 3D
        fig.update_layout(
            title=dict(
                text=config.title or f'3D Surface Plot: {column_z}',
                font=dict(size=16, family='Arial, sans-serif')
            ),
            scene=dict(
                xaxis_title=config.xlabel or column_x,
                yaxis_title=config.ylabel or column_y,
                zaxis_title=column_z,
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.3)
                )
            ),
            template='plotly_white',
            showlegend=True,
            width=900,
            height=700,
            margin=dict(l=0, r=0, t=100, b=0)
        )

        return fig

    def render_with_metrics(self,
                           data: pd.DataFrame,
                           config: RenderConfig,
                           analysis_result: AnalysisResult,
                           **kwargs) -> go.Figure:
        """
        Render contour plot with metrics in title

        Args:
            data: DataFrame with 3 columns
            config: Rendering configuration
            analysis_result: Analysis results to display
            **kwargs: Additional parameters

        Returns:
            Plotly Figure with metrics
        """
        # Render base plot
        fig = self.render(data, config, analysis_result, **kwargs)

        # Get column name and metrics
        column_z = kwargs.get('column_z', data.columns[2])
        z_min = analysis_result.get_metric('z_min', 0)
        z_max = analysis_result.get_metric('z_max', 0)
        z_mean = analysis_result.get_metric('z_mean', 0)
        n_points = analysis_result.get_metric('n_points', 0)

        # Update title with metrics
        plot_3d = kwargs.get('plot_3d', False)
        plot_type = '3D Surface' if plot_3d else 'Contour'

        title_text = (
            f'<b>{plot_type} Plot: {column_z}</b><br>'
            f'<span style="font-size:12px">'
            f'Min = {z_min:.2f}  |  Max = {z_max:.2f}  |  '
            f'Mean = {z_mean:.2f}  |  n = {n_points}'
            f'</span>'
        )

        fig.update_layout(title=dict(text=title_text))

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
        """Get renderer type"""
        return self._renderer_type
