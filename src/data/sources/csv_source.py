"""CSV data source implementation"""
import os
from pathlib import Path
import pandas as pd
from src.core.interfaces.data_source import IDataSource


class CSVDataSource(IDataSource):
    """CSV file data source implementation"""

    def __init__(self):
        """Initialize CSV data source"""
        self._supported_extensions = ['.csv', '.tsv', '.txt']

    def load(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Load data from CSV file

        Args:
            file_path: Path to CSV file
            **kwargs: Additional pandas read_csv parameters
                     (delimiter, encoding, etc.)

        Returns:
            pandas DataFrame containing the loaded data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.validate(file_path):
            raise ValueError(f"Unsupported file format: {file_path}")

        try:
            # Auto-detect delimiter for .tsv files
            if file_path.endswith('.tsv'):
                kwargs.setdefault('delimiter', '\t')

            # Load CSV with error handling
            df = pd.read_csv(file_path, **kwargs)

            if df.empty:
                raise ValueError("Loaded DataFrame is empty")

            return df

        except pd.errors.EmptyDataError:
            raise ValueError(f"File is empty: {file_path}")
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {str(e)}")

    def validate(self, file_path: str) -> bool:
        """
        Validate if the file is a supported CSV format

        Args:
            file_path: Path to the data file

        Returns:
            True if file extension is supported
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self._supported_extensions

    def get_supported_extensions(self) -> list[str]:
        """
        Get list of supported file extensions

        Returns:
            List of supported extensions
        """
        return self._supported_extensions.copy()
