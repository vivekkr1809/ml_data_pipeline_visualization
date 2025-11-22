"""PCA latent space analysis implementation"""
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import List, Optional
from src.core.interfaces.analyzer import IAnalyzer, AnalysisResult
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class PCAAnalyzer(IAnalyzer):
    """
    Analyzer for PCA dimensionality reduction
    Reduces high-dimensional data to 2D or 3D latent space
    """

    def __init__(self):
        """Initialize PCA analyzer"""
        self._required_columns = 2  # Minimum for analysis
        logger.debug("PCAAnalyzer initialized")

    def analyze(self, data: pd.DataFrame, **kwargs) -> AnalysisResult:
        """
        Perform PCA analysis

        Args:
            data: DataFrame with feature columns
            **kwargs: Optional parameters
                - feature_columns: List of column names to use as features
                - n_components: Number of components (2 or 3, default: 2)
                - standardize: Whether to standardize features (default: True)
                - target_column: Optional column for labeling (not used in PCA)

        Returns:
            AnalysisResult with transformed coordinates and PCA metrics

        Raises:
            ValueError: If data is invalid
        """
        logger.info("Starting PCA analysis")

        if not self.validate_data(data, **kwargs):
            raise ValueError("Invalid data for PCA analysis")

        # Extract parameters
        feature_columns = kwargs.get('feature_columns')
        n_components = kwargs.get('n_components', 2)
        standardize = kwargs.get('standardize', True)
        target_column = kwargs.get('target_column', None)

        if feature_columns is None:
            # Use all numeric columns except target
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            if target_column and target_column in numeric_cols:
                numeric_cols.remove(target_column)
            feature_columns = numeric_cols

        logger.info(f"Using {len(feature_columns)} feature columns for PCA")
        logger.debug(f"Feature columns: {feature_columns}")
        logger.debug(f"Components: {n_components}, Standardize: {standardize}")

        # Extract features
        X = data[feature_columns].values

        # Remove rows with NaN
        mask = ~np.isnan(X).any(axis=1)
        X_clean = X[mask]

        if len(X_clean) < 2:
            raise ValueError("Insufficient data points for PCA (need at least 2)")

        logger.info(f"Data shape: {X_clean.shape}, Removed {len(X) - len(X_clean)} rows with NaN")

        # Standardize if requested
        if standardize:
            logger.debug("Standardizing features")
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_clean)
        else:
            X_scaled = X_clean

        # Perform PCA
        logger.debug(f"Fitting PCA with {n_components} components")
        pca = PCA(n_components=n_components)
        X_transformed = pca.fit_transform(X_scaled)

        logger.info(f"PCA completed. Explained variance: {pca.explained_variance_ratio_}")

        # Prepare coordinates
        pc1 = X_transformed[:, 0]
        pc2 = X_transformed[:, 1]
        pc3 = X_transformed[:, 2] if n_components >= 3 else None

        # Extract target labels if provided
        target_labels = None
        if target_column and target_column in data.columns:
            target_labels = data[target_column].values[mask]
            logger.debug(f"Using target column: {target_column}")

        # Calculate metrics
        explained_variance = pca.explained_variance_ratio_.tolist()
        cumulative_variance = np.cumsum(explained_variance).tolist()

        metrics = {
            'n_components': n_components,
            'n_features': len(feature_columns),
            'n_samples': len(X_clean),
            'n_removed': len(X) - len(X_clean),
            'explained_variance': explained_variance,
            'cumulative_variance': cumulative_variance,
            'total_variance_explained': float(np.sum(explained_variance)),
            'standardized': standardize
        }

        metadata = {
            'feature_columns': feature_columns,
            'target_column': target_column,
            'pc1': pc1,
            'pc2': pc2,
            'pc3': pc3,
            'target_labels': target_labels,
            'pca_components': pca.components_,  # Eigenvectors
            'original_mask': mask  # Track which rows were kept
        }

        logger.info(f"PCA metrics: {metrics}")

        return AnalysisResult(metrics=metrics, metadata=metadata)

    def validate_data(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        Validate if data is suitable for PCA analysis

        Args:
            data: DataFrame to validate
            **kwargs: Optional column specifications

        Returns:
            True if data is valid
        """
        if data is None or data.empty:
            logger.warning("Data is None or empty")
            return False

        feature_columns = kwargs.get('feature_columns')

        if feature_columns is None:
            # Check if there are enough numeric columns
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) < self._required_columns:
                logger.warning(f"Not enough numeric columns: {len(numeric_cols)} < {self._required_columns}")
                return False
        else:
            # Validate specified columns
            if len(feature_columns) < self._required_columns:
                logger.warning(f"Not enough feature columns specified: {len(feature_columns)}")
                return False

            for col in feature_columns:
                if col not in data.columns:
                    logger.warning(f"Feature column not found: {col}")
                    return False
                if not pd.api.types.is_numeric_dtype(data[col]):
                    logger.warning(f"Feature column is not numeric: {col}")
                    return False

        # Need at least 2 samples
        if len(data) < 2:
            logger.warning(f"Not enough samples: {len(data)} < 2")
            return False

        return True

    def get_required_columns(self) -> int:
        """
        Get the number of required columns

        Returns:
            Minimum number of required columns (2 for PCA)
        """
        return self._required_columns
