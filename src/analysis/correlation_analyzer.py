"""Correlation analysis implementation"""
import numpy as np
import pandas as pd
from scipy import stats
from typing import List
from src.core.interfaces.analyzer import IAnalyzer, AnalysisResult


class CorrelationAnalyzer(IAnalyzer):
    """
    Analyzer for correlation between two variables
    Calculates slope, R², RMSE, and other linearity metrics
    """

    def __init__(self):
        """Initialize correlation analyzer"""
        self._required_columns = 2

    def analyze(self, data: pd.DataFrame, **kwargs) -> AnalysisResult:
        """
        Perform correlation analysis

        Args:
            data: DataFrame with exactly 2 columns (x, y)
            **kwargs: Optional parameters
                - column_x: Name of x column (default: first column)
                - column_y: Name of y column (default: second column)

        Returns:
            AnalysisResult with metrics: slope, intercept, r2, rmse,
                                        pearson_r, p_value, std_error

        Raises:
            ValueError: If data is invalid
        """
        if not self.validate_data(data, **kwargs):
            raise ValueError("Invalid data for correlation analysis")

        # Extract columns
        column_x = kwargs.get('column_x', data.columns[0])
        column_y = kwargs.get('column_y', data.columns[1])

        if column_x not in data.columns or column_y not in data.columns:
            raise ValueError(f"Columns {column_x} or {column_y} not found in data")

        # Get clean data (remove NaN values)
        # Handle case where x and y are the same column
        if column_x == column_y:
            clean_data = data[[column_x]].dropna()
            x = clean_data[column_x].values
            y = clean_data[column_x].values
        else:
            clean_data = data[[column_x, column_y]].dropna()
            x = clean_data[column_x].values
            y = clean_data[column_y].values

        if len(clean_data) < 2:
            raise ValueError("Insufficient data points for analysis (need at least 2)")

        # Calculate linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        # Calculate predictions and residuals
        y_pred = slope * x + intercept
        residuals = y - y_pred

        # Calculate RMSE
        rmse = np.sqrt(np.mean(residuals ** 2))

        # Calculate R²
        r2 = r_value ** 2

        # Calculate additional metrics
        mae = np.mean(np.abs(residuals))
        mse = np.mean(residuals ** 2)

        metrics = {
            'slope': float(slope),
            'intercept': float(intercept),
            'r2': float(r2),
            'rmse': float(rmse),
            'pearson_r': float(r_value),
            'p_value': float(p_value),
            'std_error': float(std_err),
            'mae': float(mae),
            'mse': float(mse),
            'n_points': len(clean_data),
            'n_removed': len(data) - len(clean_data)
        }

        metadata = {
            'column_x': column_x,
            'column_y': column_y,
            'x_range': (float(x.min()), float(x.max())),
            'y_range': (float(y.min()), float(y.max()))
        }

        return AnalysisResult(metrics=metrics, metadata=metadata)

    def validate_data(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        Validate if data is suitable for correlation analysis

        Args:
            data: DataFrame to validate
            **kwargs: Optional column specifications

        Returns:
            True if data is valid
        """
        if data is None or data.empty:
            return False

        # Check if specified columns exist and are numeric
        column_x = kwargs.get('column_x', data.columns[0] if len(data.columns) > 0 else None)
        column_y = kwargs.get('column_y', data.columns[1] if len(data.columns) > 1 else data.columns[0] if len(data.columns) > 0 else None)

        if column_x is None or column_y is None:
            return False

        if column_x not in data.columns or column_y not in data.columns:
            return False

        # Check if columns are numeric
        if not pd.api.types.is_numeric_dtype(data[column_x]):
            return False
        if not pd.api.types.is_numeric_dtype(data[column_y]):
            return False

        # Need at least 2 data points
        # Handle case where x and y are the same column
        if column_x == column_y:
            clean_data = data[[column_x]].dropna()
        else:
            clean_data = data[[column_x, column_y]].dropna()

        if len(clean_data) < 2:
            return False

        return True

    def get_required_columns(self) -> int:
        """
        Get the number of required columns

        Returns:
            Number of required columns (2 for correlation)
        """
        return self._required_columns
