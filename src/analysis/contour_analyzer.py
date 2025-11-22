"""Contour analysis implementation for 3D data"""
import numpy as np
import pandas as pd
from scipy import interpolate
from typing import Tuple
from src.core.interfaces.analyzer import IAnalyzer, AnalysisResult


class ContourAnalyzer(IAnalyzer):
    """
    Analyzer for 3D contour data (X, Y, Z)
    Calculates surface statistics and interpolation
    """

    def __init__(self):
        """Initialize contour analyzer"""
        self._required_columns = 3

    def analyze(self, data: pd.DataFrame, **kwargs) -> AnalysisResult:
        """
        Perform contour analysis

        Args:
            data: DataFrame with 3 columns (x, y, z)
            **kwargs: Optional parameters
                - column_x: Name of x column (default: first column)
                - column_y: Name of y column (default: second column)
                - column_z: Name of z column (default: third column)
                - interpolation_method: 'linear' or 'cubic' (default: 'linear')
                - grid_resolution: Resolution for interpolation grid (default: 50)

        Returns:
            AnalysisResult with surface statistics and interpolated grid

        Raises:
            ValueError: If data is invalid
        """
        if not self.validate_data(data, **kwargs):
            raise ValueError("Invalid data for contour analysis")

        # Extract columns
        column_x = kwargs.get('column_x', data.columns[0])
        column_y = kwargs.get('column_y', data.columns[1])
        column_z = kwargs.get('column_z', data.columns[2])

        if column_x not in data.columns or column_y not in data.columns or column_z not in data.columns:
            raise ValueError(f"Columns {column_x}, {column_y}, or {column_z} not found in data")

        # Get clean data (remove NaN values)
        clean_data = data[[column_x, column_y, column_z]].dropna()

        if len(clean_data) < 3:
            raise ValueError("Insufficient data points for contour analysis (need at least 3)")

        x = clean_data[column_x].values
        y = clean_data[column_y].values
        z = clean_data[column_z].values

        # Calculate statistics
        z_min = float(np.min(z))
        z_max = float(np.max(z))
        z_mean = float(np.mean(z))
        z_std = float(np.std(z))
        z_range = z_max - z_min

        # Calculate gradient (rate of change)
        if len(x) > 1:
            dx = np.diff(x) if len(np.unique(x)) > 1 else np.ones(len(x) - 1)
            dy = np.diff(y) if len(np.unique(y)) > 1 else np.ones(len(y) - 1)
            dz = np.diff(z)

            # Average gradient magnitude
            gradient_x = np.abs(dz / (dx + 1e-10))
            gradient_y = np.abs(dz / (dy + 1e-10))
            avg_gradient = float(np.mean(np.sqrt(gradient_x**2 + gradient_y**2)))
        else:
            avg_gradient = 0.0

        # Grid interpolation for smooth contours
        grid_resolution = kwargs.get('grid_resolution', 50)
        interpolation_method = kwargs.get('interpolation_method', 'linear')

        try:
            # Create regular grid
            xi = np.linspace(x.min(), x.max(), grid_resolution)
            yi = np.linspace(y.min(), y.max(), grid_resolution)
            xi_grid, yi_grid = np.meshgrid(xi, yi)

            # Interpolate Z values on grid
            if interpolation_method == 'cubic' and len(x) > 9:
                # Cubic requires more points
                zi_grid = interpolate.griddata(
                    (x, y), z, (xi_grid, yi_grid), method='cubic', fill_value=np.nan
                )
                # Fill NaN values with linear interpolation
                zi_grid_linear = interpolate.griddata(
                    (x, y), z, (xi_grid, yi_grid), method='linear', fill_value=z_mean
                )
                zi_grid = np.where(np.isnan(zi_grid), zi_grid_linear, zi_grid)
            else:
                zi_grid = interpolate.griddata(
                    (x, y), z, (xi_grid, yi_grid), method='linear', fill_value=z_mean
                )

        except Exception as e:
            raise ValueError(f"Interpolation failed: {str(e)}")

        metrics = {
            'z_min': z_min,
            'z_max': z_max,
            'z_mean': z_mean,
            'z_std': z_std,
            'z_range': z_range,
            'avg_gradient': avg_gradient,
            'n_points': len(clean_data),
            'n_removed': len(data) - len(clean_data),
            'interpolation_method': interpolation_method
        }

        metadata = {
            'column_x': column_x,
            'column_y': column_y,
            'column_z': column_z,
            'x_range': (float(x.min()), float(x.max())),
            'y_range': (float(y.min()), float(y.max())),
            'z_range': (z_min, z_max),
            'grid_x': xi,
            'grid_y': yi,
            'grid_z': zi_grid,
            'original_x': x,
            'original_y': y,
            'original_z': z
        }

        return AnalysisResult(metrics=metrics, metadata=metadata)

    def validate_data(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        Validate if data is suitable for contour analysis

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
        column_y = kwargs.get('column_y', data.columns[1] if len(data.columns) > 1 else None)
        column_z = kwargs.get('column_z', data.columns[2] if len(data.columns) > 2 else None)

        if column_x is None or column_y is None or column_z is None:
            return False

        if column_x not in data.columns or column_y not in data.columns or column_z not in data.columns:
            return False

        # Check if columns are numeric
        if not pd.api.types.is_numeric_dtype(data[column_x]):
            return False
        if not pd.api.types.is_numeric_dtype(data[column_y]):
            return False
        if not pd.api.types.is_numeric_dtype(data[column_z]):
            return False

        # Need at least 3 data points for contour
        clean_data = data[[column_x, column_y, column_z]].dropna()
        if len(clean_data) < 3:
            return False

        return True

    def get_required_columns(self) -> int:
        """
        Get the number of required columns

        Returns:
            Number of required columns (3 for contour)
        """
        return self._required_columns
