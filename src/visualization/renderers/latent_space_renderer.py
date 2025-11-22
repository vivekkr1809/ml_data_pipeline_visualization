"""Matplotlib-based latent space visualization renderer"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from typing import Optional
from src.core.interfaces.renderer import IRenderer, RenderConfig
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class LatentSpaceRenderer(IRenderer):
    """
    Renderer for latent space visualizations (PCA, t-SNE)
    Creates 2D or 3D scatter plots of transformed data
    """

    def __init__(self):
        """Initialize latent space renderer"""
        logger.debug("LatentSpaceRenderer initialized")

    def get_renderer_type(self) -> str:
        """Get the type of renderer"""
        return "latent_space_matplotlib"

    def validate_data(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        Validate if data is suitable for latent space rendering

        Args:
            data: DataFrame to validate
            **kwargs: Must contain dim1 and dim2 arrays

        Returns:
            True if data is valid
        """
        # For latent space, we validate the transformed coordinates, not the original data
        dim1 = kwargs.get('dim1')
        dim2 = kwargs.get('dim2')

        if dim1 is None or dim2 is None:
            return False

        if len(dim1) == 0 or len(dim2) == 0:
            return False

        if len(dim1) != len(dim2):
            return False

        return True

    def render(self, data: pd.DataFrame, config: RenderConfig, **kwargs) -> Figure:
        """
        Render latent space visualization

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
            Matplotlib Figure
        """
        logger.info("Rendering latent space visualization")

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
        if is_3d:
            fig = Figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            logger.debug("Creating 3D scatter plot")
        else:
            fig = Figure(figsize=(10, 8))
            ax = fig.add_subplot(111)
            logger.debug("Creating 2D scatter plot")

        # Prepare colors
        colors, unique_labels, cmap = self._prepare_colors(target_labels)

        # Create scatter plot
        if is_3d:
            scatter = ax.scatter(dim1, dim2, dim3, c=colors, cmap=cmap,
                               alpha=0.7, s=50, edgecolors='black', linewidth=0.5)
            ax.set_zlabel('Component 3' if analysis_type == 'pca' else 'Dimension 3',
                         fontsize=10)
        else:
            scatter = ax.scatter(dim1, dim2, c=colors, cmap=cmap,
                               alpha=0.7, s=50, edgecolors='black', linewidth=0.5)

        # Set labels based on analysis type
        if analysis_type == 'pca':
            # Add explained variance to axis labels if available
            var1 = metrics.get('explained_variance', [0, 0])[0] * 100
            var2 = metrics.get('explained_variance', [0, 0, 0])[1] * 100 if len(metrics.get('explained_variance', [])) > 1 else 0

            ax.set_xlabel(f'PC1 ({var1:.1f}% variance)', fontsize=10)
            ax.set_ylabel(f'PC2 ({var2:.1f}% variance)', fontsize=10)

            # Add title with total explained variance
            total_var = sum(metrics.get('explained_variance', [])[:3 if is_3d else 2]) * 100
            title = f'PCA Latent Space\n({total_var:.1f}% total variance explained)'
        else:
            ax.set_xlabel('Dimension 1', fontsize=10)
            ax.set_ylabel('Dimension 2', fontsize=10)

            # Add KL divergence if available
            kl_div = metrics.get('kl_divergence')
            if kl_div is not None:
                title = f't-SNE Latent Space\n(KL divergence: {kl_div:.4f})'
            else:
                title = 't-SNE Latent Space'

        ax.set_title(title, fontsize=12, fontweight='bold')

        # Add legend if we have categorical labels
        if target_labels is not None and unique_labels is not None:
            if len(unique_labels) <= 20:  # Only show legend if not too many categories
                if isinstance(unique_labels[0], (int, float, np.integer, np.floating)):
                    # Numeric labels - use colorbar
                    cbar = fig.colorbar(scatter, ax=ax, pad=0.1)
                    cbar.set_label('Target Value', fontsize=10)
                else:
                    # Categorical labels - use legend
                    legend_elements = [
                        Patch(facecolor=plt.cm.get_cmap(cmap)(i / len(unique_labels)),
                             label=str(label))
                        for i, label in enumerate(unique_labels)
                    ]
                    ax.legend(handles=legend_elements, loc='best', fontsize=8,
                            title='Target', framealpha=0.9)
                logger.debug(f"Added legend with {len(unique_labels)} categories")

        # Add grid
        ax.grid(True, alpha=0.3)

        # Add metadata text
        metadata_text = self._format_metadata(metrics, len(dim1))
        fig.text(0.02, 0.02, metadata_text, fontsize=8, family='monospace',
                verticalalignment='bottom', bbox=dict(boxstyle='round',
                facecolor='wheat', alpha=0.3))

        fig.tight_layout()
        logger.info("Latent space visualization rendered successfully")

        return fig

    def _prepare_colors(self, target_labels):
        """
        Prepare colors for scatter plot based on target labels

        Args:
            target_labels: Array of labels or None

        Returns:
            tuple: (colors, unique_labels, colormap_name)
        """
        if target_labels is None:
            return '#2E86AB', None, None

        # Check if numeric or categorical
        try:
            # Try to convert to numeric
            numeric_labels = pd.to_numeric(target_labels)
            logger.debug("Labels are numeric, using continuous colormap")
            return numeric_labels, None, 'viridis'
        except (ValueError, TypeError):
            # Categorical labels
            unique_labels = np.unique(target_labels)
            logger.debug(f"Labels are categorical with {len(unique_labels)} unique values")

            # Create color mapping
            label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
            colors = np.array([label_to_idx[label] for label in target_labels])

            return colors, unique_labels, 'tab10'

    def _format_metadata(self, metrics: dict, n_points: int) -> str:
        """
        Format metadata for display

        Args:
            metrics: Metrics dictionary
            n_points: Number of data points

        Returns:
            Formatted string
        """
        lines = [f"N = {n_points}"]

        if 'n_features' in metrics:
            lines.append(f"Features = {metrics['n_features']}")

        if 'n_removed' in metrics and metrics['n_removed'] > 0:
            lines.append(f"Removed (NaN) = {metrics['n_removed']}")

        return ' | '.join(lines)
