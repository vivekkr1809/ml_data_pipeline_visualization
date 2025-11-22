"""Analyzer interface - Strategy pattern for different analysis types"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd


class AnalysisResult:
    """Container for analysis results"""

    def __init__(self, metrics: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize analysis result

        Args:
            metrics: Dictionary of calculated metrics
            metadata: Optional metadata about the analysis
        """
        self.metrics = metrics
        self.metadata = metadata or {}

    def get_metric(self, name: str, default: Any = None) -> Any:
        """Get a specific metric value"""
        return self.metrics.get(name, default)

    def __repr__(self) -> str:
        return f"AnalysisResult(metrics={self.metrics})"


class IAnalyzer(ABC):
    """Interface for data analyzers following Single Responsibility Principle"""

    @abstractmethod
    def analyze(self, data: pd.DataFrame, **kwargs) -> AnalysisResult:
        """
        Perform analysis on data

        Args:
            data: DataFrame to analyze
            **kwargs: Analysis-specific parameters

        Returns:
            AnalysisResult containing metrics and metadata

        Raises:
            ValueError: If data is invalid for this analysis
        """
        pass

    @abstractmethod
    def validate_data(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        Validate if data is suitable for this analysis

        Args:
            data: DataFrame to validate
            **kwargs: Validation parameters

        Returns:
            True if data is valid
        """
        pass

    @abstractmethod
    def get_required_columns(self) -> int:
        """
        Get the number of required columns for this analysis

        Returns:
            Number of required columns
        """
        pass
