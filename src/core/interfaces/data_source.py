"""Data source interface - Strategy pattern for different file types"""
from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class IDataSource(ABC):
    """Interface for data sources following Open/Closed Principle"""

    @abstractmethod
    def load(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Load data from a source

        Args:
            file_path: Path to the data file
            **kwargs: Additional parameters specific to the data source

        Returns:
            pandas DataFrame containing the loaded data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        pass

    @abstractmethod
    def validate(self, file_path: str) -> bool:
        """
        Validate if the file can be loaded by this data source

        Args:
            file_path: Path to the data file

        Returns:
            True if file is valid for this data source
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """
        Get list of supported file extensions

        Returns:
            List of file extensions (e.g., ['.csv', '.tsv'])
        """
        pass
