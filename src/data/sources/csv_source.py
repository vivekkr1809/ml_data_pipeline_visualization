"""CSV data source implementation"""
import os
from pathlib import Path
import pandas as pd
from src.core.interfaces.data_source import IDataSource
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CSVDataSource(IDataSource):
    """CSV file data source implementation"""

    def __init__(self):
        """Initialize CSV data source"""
        self._supported_extensions = ['.csv', '.tsv', '.txt']
        logger.debug(f"CSVDataSource initialized with extensions: {self._supported_extensions}")

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
        logger.info(f"Loading CSV file: {file_path}")
        logger.debug(f"Load parameters: {kwargs}")

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.validate(file_path):
            logger.error(f"Unsupported file format: {file_path}")
            raise ValueError(f"Unsupported file format: {file_path}")

        try:
            # Auto-detect delimiter for .tsv files
            if file_path.endswith('.tsv'):
                kwargs.setdefault('delimiter', '\t')
                logger.debug("Auto-detected TSV format, using tab delimiter")

            # Load CSV with error handling
            df = pd.read_csv(file_path, **kwargs)

            if df.empty:
                logger.error(f"Loaded DataFrame is empty from: {file_path}")
                raise ValueError("Loaded DataFrame is empty")

            logger.info(f"Successfully loaded CSV: shape={df.shape}, columns={list(df.columns)}")
            logger.debug(f"Column types: {df.dtypes.to_dict()}")
            logger.debug(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")

            return df

        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty data error in file: {file_path}", exc_info=True)
            raise ValueError(f"File is empty: {file_path}")
        except pd.errors.ParserError as e:
            logger.error(f"Parser error in file: {file_path} - {str(e)}", exc_info=True)
            raise ValueError(f"Error parsing CSV file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error loading file: {file_path} - {str(e)}", exc_info=True)
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
