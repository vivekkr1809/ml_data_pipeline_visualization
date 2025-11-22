"""Plotly-based interactive latent space visualization renderer"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Optional
from src.core.interfaces.renderer import IRenderer, RenderConfig
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class PlotlyLatentSpaceRenderer(IRenderer):
    """
    Interactive renderer for latent space visualizations (PCA, t-SNE)
    Creates interactive 2D or 3D scatter plots using Plotly
    """

    def __init__(self):
        """Initialize Plotly latent space renderer"""
        logger.debug("PlotlyLatentSpaceRenderer initialized")

    def render(self, data: pd.DataFrame, config: RenderConfig, **kwargs) -> go.Figure:
        """
        Render interactive latent space visualization

        Args:
            data: DataFrame (not used directly, coordinates come from kwargs)
            config: Render configuration
            **kwargs: Required metadata from analyzer
                - dim1: First dimension coordinates (numpy array)
                - dim2: Second dimension coordinates (numpy array)
                - dim3: Third dimension coordinates (optional, numpy array)
                - target_labels: Optional labels for coloring points
                - analysis_type: 'pca' or 'tsne'
                - metrics: Dictionary with analysis metrics

        Returns:
            Plotly Figure
        """
        logger.info("Rendering interactive latent space visualization")

        # Extract coordinates from kwargs
        dim1 = kwargs.get('dim1')
        dim2 = kwargs.get('dim2')
        dim3 = kwargs.get('dim3')
        target_labels = kwargs.get('target_labels')
        analysis_type = kwargs.get('analysis_type', 'latent')
        metrics = kwargs.get('metrics', {})

        if dim1 is None or dim2 is None:
            raise ValueError("dim1 and dim2 coordinates are required")

        logger.debug(f"Analysis type: {analysis_type}")
        logger.debug(f"Data points: {len(dim1)}")
        logger.debug(f"3D mode: {dim3 is not None}")
        logger.debug(f"Has labels: {target_labels is not None}")

        # Determine if 3D plot
        is_3d = dim3 is not None

        # Create figure
        fig = go.Figure()

        # Prepare hover text
        hover_text = self._create_hover_text(dim1, dim2, dim3, target_labels, analysis_type)

        # Prepare colors and colorscale
        color_data, colorscale, showscale = self._prepare_colors(target_labels)

        # Create scatter plot
        if is_3d:
            logger.debug("Creating interactive 3D scatter plot")
            scatter = go.Scatter3d(
                x=dim1,
                y=dim2,
                z=dim3,
                mode='markers',
                marker=dict(
                    size=5,
                    color=color_data,
                    colorscale=colorscale if colorscale else 'Viridis',
                    showscale=showscale,
                    line=dict(width=0.5, color='white'),
                    opacity=0.8,
                    colorbar=dict(title='Target') if showscale else None
                ),
                text=hover_text,
                hovertemplate='<b>%{text}</b><br>' +
                             'Dim1: %{x:.3f}<br>' +
                             'Dim2: %{y:.3f}<br>' +
                             'Dim3: %{z:.3f}<br>' +
                             '<extra></extra>',
                name='Data Points'
            )
        else:
            logger.debug("Creating interactive 2D scatter plot")
            scatter = go.Scatter(
                x=dim1,
                y=dim2,
                mode='markers',
                marker=dict(
                    size=8,
                    color=color_data,
                    colorscale=colorscale if colorscale else 'Viridis',
                    showscale=showscale,
                    line=dict(width=0.5, color='white'),
                    opacity=0.8,
                    colorbar=dict(title='Target') if showscale else None
                ),
                text=hover_text,
                hovertemplate='<b>%{text}</b><br>' +
                             'Dim1: %{x:.3f}<br>' +
                             'Dim2: %{y:.3f}<br>' +
                             '<extra></extra>',
                name='Data Points'
            )

        fig.add_trace(scatter)

        # Set axis labels and title based on analysis type
        if analysis_type == 'pca':
            # Add explained variance to axis labels if available
            var1 = metrics.get('explained_variance', [0, 0])[0] * 100
            var2 = metrics.get('explained_variance', [0, 0, 0])[1] * 100 if len(metrics.get('explained_variance', [])) > 1 else 0

            xlabel = f'PC1 ({var1:.1f}% variance)'
            ylabel = f'PC2 ({var2:.1f}% variance)'

            # Add title with total explained variance
            total_var = sum(metrics.get('explained_variance', [])[:3 if is_3d else 2]) * 100
            title = f'PCA Latent Space ({total_var:.1f}% total variance explained)'

            if is_3d:
                var3 = metrics.get('explained_variance', [0, 0, 0])[2] * 100 if len(metrics.get('explained_variance', [])) > 2 else 0
                zlabel = f'PC3 ({var3:.1f}% variance)'
        else:
            xlabel = 'Dimension 1'
            ylabel = 'Dimension 2'

            # Add KL divergence if available
            kl_div = metrics.get('kl_divergence')
            if kl_div is not None:
                title = f't-SNE Latent Space (KL divergence: {kl_div:.4f})'
            else:
                title = 't-SNE Latent Space'

            if is_3d:
                zlabel = 'Dimension 3'

        # Update layout
        if is_3d:
            fig.update_layout(
                title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16)),
                scene=dict(
                    xaxis=dict(title=xlabel, gridcolor='lightgray', showbackground=True),
                    yaxis=dict(title=ylabel, gridcolor='lightgray', showbackground=True),
                    zaxis=dict(title=zlabel, gridcolor='lightgray', showbackground=True),
                    bgcolor='white'
                ),
                width=900,
                height=700,
                hovermode='closest',
                showlegend=False
            )
        else:
            fig.update_layout(
                title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16)),
                xaxis=dict(title=xlabel, gridcolor='lightgray', showgrid=True),
                yaxis=dict(title=ylabel, gridcolor='lightgray', showgrid=True),
                width=900,
                height=700,
                hovermode='closest',
                plot_bgcolor='white',
                showlegend=False
            )

        # Add annotations with metadata
        annotation_text = self._format_metadata(metrics, len(dim1))
        fig.add_annotation(
            text=annotation_text,
            xref='paper', yref='paper',
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor='rgba(255, 255, 200, 0.8)',
            bordercolor='gray',
            borderwidth=1,
            font=dict(size=10, family='monospace'),
            align='left',
            xanchor='left',
            yanchor='top'
        )

        logger.info("Interactive latent space visualization rendered successfully")

        return fig

    def _create_hover_text(self, dim1, dim2, dim3, target_labels, analysis_type):
        """
        Create hover text for each point

        Args:
            dim1, dim2, dim3: Coordinate arrays
            target_labels: Optional labels
            analysis_type: Type of analysis

        Returns:
            List of hover text strings
        """
        hover_text = []
        for i in range(len(dim1)):
            if target_labels is not None:
                text = f"Point {i}<br>Label: {target_labels[i]}"
            else:
                text = f"Point {i}"
            hover_text.append(text)

        return hover_text

    def _prepare_colors(self, target_labels):
        """
        Prepare colors for scatter plot based on target labels

        Args:
            target_labels: Array of labels or None

        Returns:
            tuple: (color_data, colorscale, showscale)
        """
        if target_labels is None:
            return '#2E86AB', None, False

        # Check if numeric or categorical
        try:
            # Try to convert to numeric
            numeric_labels = pd.to_numeric(target_labels)
            logger.debug("Labels are numeric, using continuous colormap")
            return numeric_labels, 'Viridis', True
        except (ValueError, TypeError):
            # Categorical labels
            unique_labels = np.unique(target_labels)
            logger.debug(f"Labels are categorical with {len(unique_labels)} unique values")

            # Create color mapping
            label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
            colors = [label_to_idx[label] for label in target_labels]

            # Use discrete colorscale
            return colors, 'Plotly3', True

    def _format_metadata(self, metrics: dict, n_points: int) -> str:
        """
        Format metadata for display

        Args:
            metrics: Metrics dictionary
            n_points: Number of data points

        Returns:
            Formatted string
        """
        lines = [f"<b>Metadata</b>"]
        lines.append(f"Points: {n_points}")

        if 'n_features' in metrics:
            lines.append(f"Features: {metrics['n_features']}")

        if 'n_removed' in metrics and metrics['n_removed'] > 0:
            lines.append(f"Removed (NaN): {metrics['n_removed']}")

        if 'perplexity' in metrics:
            lines.append(f"Perplexity: {metrics['perplexity']}")

        if 'standardized' in metrics:
            lines.append(f"Standardized: {metrics['standardized']}")

        return '<br>'.join(lines)
