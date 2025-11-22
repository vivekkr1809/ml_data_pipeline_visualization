"""t-SNE latent space analysis implementation"""
import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from typing import List, Optional
from src.core.interfaces.analyzer import IAnalyzer, AnalysisResult
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class TSNEAnalyzer(IAnalyzer):
    """
    Analyzer for t-SNE dimensionality reduction
    Reduces high-dimensional data to 2D or 3D latent space
    """

    def __init__(self):
        """Initialize t-SNE analyzer"""
        self._required_columns = 2  # Minimum for analysis
        logger.debug("TSNEAnalyzer initialized")

    def analyze(self, data: pd.DataFrame, **kwargs) -> AnalysisResult:
        """
        Perform t-SNE analysis

        Args:
            data: DataFrame with feature columns
            **kwargs: Optional parameters
                - feature_columns: List of column names to use as features
                - n_components: Number of components (2 or 3, default: 2)
                - perplexity: t-SNE perplexity parameter (default: 30)
                - n_iter: Number of iterations (default: 1000)
                - learning_rate: Learning rate (default: 200)
                - standardize: Whether to standardize features (default: True)
                - target_column: Optional column for labeling (not used in t-SNE)
                - random_state: Random seed for reproducibility (default: 42)

        Returns:
            AnalysisResult with transformed coordinates and t-SNE metrics

        Raises:
            ValueError: If data is invalid
        """
        logger.info("Starting t-SNE analysis")

        if not self.validate_data(data, **kwargs):
            raise ValueError("Invalid data for t-SNE analysis")

        # Extract parameters
        feature_columns = kwargs.get('feature_columns')
        n_components = kwargs.get('n_components', 2)
        perplexity = kwargs.get('perplexity', 30)
        n_iter = kwargs.get('n_iter', 1000)
        learning_rate = kwargs.get('learning_rate', 200)
        standardize = kwargs.get('standardize', True)
        target_column = kwargs.get('target_column', None)
        random_state = kwargs.get('random_state', 42)

        if feature_columns is None:
            # Use all numeric columns except target
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            if target_column and target_column in numeric_cols:
                numeric_cols.remove(target_column)
            feature_columns = numeric_cols

        logger.info(f"Using {len(feature_columns)} feature columns for t-SNE")
        logger.debug(f"Feature columns: {feature_columns}")
        logger.debug(f"Components: {n_components}, Perplexity: {perplexity}, Iterations: {n_iter}")

        # Extract features
        X = data[feature_columns].values

        # Remove rows with NaN
        mask = ~np.isnan(X).any(axis=1)
        X_clean = X[mask]

        if len(X_clean) < perplexity + 1:
            suggested_perplexity = max(5, len(X_clean) // 3)
            logger.warning(f"Perplexity too large for sample size. Adjusting from {perplexity} to {suggested_perplexity}")
            perplexity = suggested_perplexity

        if len(X_clean) < 2:
            raise ValueError("Insufficient data points for t-SNE (need at least 2)")

        logger.info(f"Data shape: {X_clean.shape}, Removed {len(X) - len(X_clean)} rows with NaN")

        # Standardize if requested
        if standardize:
            logger.debug("Standardizing features")
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_clean)
        else:
            X_scaled = X_clean

        # Perform t-SNE
        logger.debug(f"Fitting t-SNE with {n_components} components")
        logger.info("t-SNE computation started (this may take a while...)")

        tsne = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            max_iter=n_iter,  # Changed from n_iter to max_iter for scikit-learn compatibility
            learning_rate=learning_rate,
            random_state=random_state,
            verbose=0
        )

        X_transformed = tsne.fit_transform(X_scaled)

        logger.info(f"t-SNE completed. KL divergence: {tsne.kl_divergence_:.4f}")

        # Prepare coordinates
        dim1 = X_transformed[:, 0]
        dim2 = X_transformed[:, 1]
        dim3 = X_transformed[:, 2] if n_components >= 3 else None

        # Extract target labels if provided
        target_labels = None
        if target_column and target_column in data.columns:
            target_labels = data[target_column].values[mask]
            logger.debug(f"Using target column: {target_column}")

        # Calculate metrics
        metrics = {
            'n_components': n_components,
            'n_features': len(feature_columns),
            'n_samples': len(X_clean),
            'n_removed': len(X) - len(X_clean),
            'perplexity': perplexity,
            'n_iter': n_iter,
            'learning_rate': learning_rate,
            'kl_divergence': float(tsne.kl_divergence_),
            'standardized': standardize,
            'random_state': random_state
        }

        metadata = {
            'feature_columns': feature_columns,
            'target_column': target_column,
            'dim1': dim1,
            'dim2': dim2,
            'dim3': dim3,
            'target_labels': target_labels,
            'original_mask': mask  # Track which rows were kept
        }

        logger.info(f"t-SNE metrics: {metrics}")

        return AnalysisResult(metrics=metrics, metadata=metadata)

    def validate_data(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        Validate if data is suitable for t-SNE analysis

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
        perplexity = kwargs.get('perplexity', 30)

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

        # Need enough samples for perplexity
        if len(data) < max(2, perplexity + 1):
            logger.warning(f"Not enough samples for perplexity {perplexity}: {len(data)}")
            # Don't fail, just warn - we'll adjust perplexity in analyze()
            return len(data) >= 2

        return True

    def get_required_columns(self) -> int:
        """
        Get the number of required columns

        Returns:
            Minimum number of required columns (2 for t-SNE)
        """
        return self._required_columns
