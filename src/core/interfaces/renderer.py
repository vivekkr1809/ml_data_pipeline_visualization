"""Renderer interface - Strategy pattern for different visualization types"""
from abc import ABC, abstractmethod
from typing import Any, Optional
import pandas as pd
from matplotlib.figure import Figure


class RenderConfig:
    """Configuration for rendering"""

    def __init__(self,
                 title: Optional[str] = None,
                 xlabel: Optional[str] = None,
                 ylabel: Optional[str] = None,
                 interactive: bool = True,
                 style: Optional[str] = None,
                 **kwargs):
        """
        Initialize render configuration

        Args:
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            interactive: Enable interactive features
            style: Matplotlib style
            **kwargs: Additional renderer-specific options
        """
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.interactive = interactive
        self.style = style
        self.options = kwargs


class IRenderer(ABC):
    """Interface for plot renderers following Single Responsibility Principle"""

    @abstractmethod
    def render(self, data: pd.DataFrame, config: RenderConfig, **kwargs) -> Figure:
        """
        Render visualization

        Args:
            data: DataFrame to visualize
            config: Rendering configuration
            **kwargs: Renderer-specific parameters

        Returns:
            Matplotlib Figure object

        Raises:
            ValueError: If data is invalid for this renderer
        """
        pass

    @abstractmethod
    def validate_data(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        Validate if data is suitable for this renderer

        Args:
            data: DataFrame to validate
            **kwargs: Validation parameters

        Returns:
            True if data is valid
        """
        pass

    @abstractmethod
    def get_renderer_type(self) -> str:
        """
        Get the type of renderer

        Returns:
            String identifier for the renderer type
        """
        pass
