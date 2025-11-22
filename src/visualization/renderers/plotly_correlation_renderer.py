"""Interactive correlation plot renderer using Plotly"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional
from src.core.interfaces.renderer import RenderConfig
from src.core.interfaces.analyzer import AnalysisResult


class PlotlyCorrelationRenderer:
    """
    Interactive renderer for correlation plots using Plotly
    Returns plotly.graph_objects.Figure for interactive visualization
    """

    def __init__(self):
        """Initialize Plotly correlation renderer"""
        self._renderer_type = "plotly_correlation"

    def render(self,
               data: pd.DataFrame,
               config: RenderConfig,
               analysis_result: Optional[AnalysisResult] = None,
               **kwargs) -> go.Figure:
        """
        Render interactive correlation plot

        Args:
            data: DataFrame with 2 columns (x, y)
            config: Rendering configuration
            analysis_result: Optional pre-computed analysis results
            **kwargs: Additional parameters
                - column_x: X column name
                - column_y: Y column name
                - show_regression: Show regression line (default: True)

        Returns:
            Plotly Figure object

        Raises:
            ValueError: If data is invalid
        """
        if not self.validate_data(data, **kwargs):
            raise ValueError("Invalid data for correlation plot")

        # Extract columns
        column_x = kwargs.get('column_x', data.columns[0])
        column_y = kwargs.get('column_y', data.columns[1])

        # Get clean data
        if column_x == column_y:
            clean_data = data[[column_x]].dropna()
            x = clean_data[column_x].values
            y = clean_data[column_x].values
        else:
            clean_data = data[[column_x, column_y]].dropna()
            x = clean_data[column_x].values
            y = clean_data[column_y].values

        # Create figure
        fig = go.Figure()

        # Add scatter plot
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='markers',
            name='Data points',
            marker=dict(
                size=8,
                color='#2E86AB',
                opacity=0.7,
                line=dict(color='white', width=0.5)
            ),
            hovertemplate=f'{column_x}: %{{x:.2f}}<br>{column_y}: %{{y:.2f}}<extra></extra>'
        ))

        # Add regression line if available
        show_regression = kwargs.get('show_regression', True)
        if show_regression and analysis_result:
            slope = analysis_result.get_metric('slope')
            intercept = analysis_result.get_metric('intercept')

            if slope is not None and intercept is not None:
                x_line = np.array([x.min(), x.max()])
                y_line = slope * x_line + intercept

                fig.add_trace(go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode='lines',
                    name=f'y = {slope:.3f}x + {intercept:.3f}',
                    line=dict(color='red', width=2)
                ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=config.title or f'Correlation: {column_x} vs {column_y}',
                font=dict(size=16, family='Arial, sans-serif')
            ),
            xaxis_title=config.xlabel or column_x,
            yaxis_title=config.ylabel or column_y,
            hovermode='closest',
            template='plotly_white',
            showlegend=True,
            width=900,
            height=600,
            margin=dict(l=80, r=80, t=100, b=80)
        )

        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

        return fig

    def render_with_metrics(self,
                           data: pd.DataFrame,
                           config: RenderConfig,
                           analysis_result: AnalysisResult,
                           **kwargs) -> go.Figure:
        """
        Render interactive correlation plot with metrics annotation

        Args:
            data: DataFrame with 2 columns
            config: Rendering configuration
            analysis_result: Analysis results to display
            **kwargs: Additional parameters

        Returns:
            Plotly Figure with metrics
        """
        # Render base plot
        fig = self.render(data, config, analysis_result, **kwargs)

        # Get metrics
        r2 = analysis_result.get_metric('r2', 0)
        rmse = analysis_result.get_metric('rmse', 0)
        slope = analysis_result.get_metric('slope', 0)
        n_points = analysis_result.get_metric('n_points', 0)

        # Update title with metrics
        column_x = kwargs.get('column_x', data.columns[0])
        column_y = kwargs.get('column_y', data.columns[1])

        title_text = (
            f'<b>Correlation: {column_x} vs {column_y}</b><br>'
            f'<span style="font-size:12px">'
            f'R² = {r2:.4f}  |  RMSE = {rmse:.4f}  |  '
            f'Slope = {slope:.4f}  |  n = {n_points}'
            f'</span>'
        )

        fig.update_layout(title=dict(text=title_text))

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

        # Check specified columns
        column_x = kwargs.get('column_x', data.columns[0] if len(data.columns) > 0 else None)
        column_y = kwargs.get('column_y', data.columns[1] if len(data.columns) > 1 else data.columns[0] if len(data.columns) > 0 else None)

        if column_x is None or column_y is None:
            return False

        if column_x not in data.columns or column_y not in data.columns:
            return False

        # Check if numeric
        if not pd.api.types.is_numeric_dtype(data[column_x]):
            return False
        if not pd.api.types.is_numeric_dtype(data[column_y]):
            return False

        # Need at least 1 data point
        if column_x == column_y:
            clean_data = data[[column_x]].dropna()
        else:
            clean_data = data[[column_x, column_y]].dropna()

        if len(clean_data) < 1:
            return False

        return True

    def get_renderer_type(self) -> str:
        """Get renderer type"""
        return self._renderer_type
