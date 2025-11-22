"""Data loader widget for file selection and loading"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFileDialog, QMessageBox, QGroupBox)
from PyQt6.QtCore import pyqtSignal
import pandas as pd
from typing import Optional
from src.data.sources.csv_source import CSVDataSource
from src.data.sources.parquet_source import ParquetDataSource


class DataLoaderWidget(QWidget):
    """
    Widget for loading CSV and Parquet files
    Emits signal when data is successfully loaded
    """

    # Signal emitted when data is loaded (DataFrame, file_path)
    data_loaded = pyqtSignal(object, str)

    def __init__(self, parent=None):
        """Initialize data loader widget"""
        super().__init__(parent)
        self._csv_source = CSVDataSource()
        self._parquet_source = ParquetDataSource()
        self._current_file = None
        self._current_data = None
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()

        # Create group box
        group_box = QGroupBox("Data Loading")
        group_layout = QVBoxLayout()

        # File selection row
        file_layout = QHBoxLayout()

        self._file_label = QLabel("No file loaded")
        self._file_label.setStyleSheet("font-style: italic; color: #666;")

        self._load_button = QPushButton("Load Data File")
        self._load_button.setToolTip("Select and load a CSV or Parquet file")
        self._load_button.clicked.connect(self._on_load_clicked)

        file_layout.addWidget(self._file_label, 1)
        file_layout.addWidget(self._load_button)

        # Info label
        self._info_label = QLabel("")
        self._info_label.setStyleSheet("color: #2E86AB; font-size: 10px;")

        group_layout.addLayout(file_layout)
        group_layout.addWidget(self._info_label)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        self.setLayout(layout)

    def _on_load_clicked(self):
        """Handle load button click"""
        # Get supported extensions from both sources
        csv_exts = self._csv_source.get_supported_extensions()
        parquet_exts = self._parquet_source.get_supported_extensions()

        # Create filter string
        csv_filter = f"CSV Files (*{' *'.join(csv_exts)})"
        parquet_filter = f"Parquet Files (*{' *'.join(parquet_exts)})"
        filter_str = f"{csv_filter};;{parquet_filter};;All Files (*.*)"

        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File",
            "",
            filter_str
        )

        if file_path:
            self._load_file(file_path)

    def _load_file(self, file_path: str):
        """
        Load file and emit signal

        Args:
            file_path: Path to file to load
        """
        try:
            # Determine which data source to use based on file extension
            file_lower = file_path.lower()
            if file_lower.endswith(('.parquet', '.pq')):
                data_source = self._parquet_source
            else:
                data_source = self._csv_source

            # Load data
            data = data_source.load(file_path)

            # Update state
            self._current_file = file_path
            self._current_data = data

            # Update UI
            file_name = file_path.split('/')[-1].split('\\')[-1]
            self._file_label.setText(f"Loaded: {file_name}")
            self._file_label.setStyleSheet("color: #2E86AB; font-weight: bold;")

            rows, cols = data.shape
            self._info_label.setText(f"Shape: {rows} rows × {cols} columns")

            # Emit signal
            self.data_loaded.emit(data, file_path)

        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load file:\n{str(e)}"
            )

            # Reset UI
            self._file_label.setText("Failed to load file")
            self._file_label.setStyleSheet("color: red; font-style: italic;")
            self._info_label.setText("")

    def get_current_data(self) -> Optional[pd.DataFrame]:
        """Get currently loaded data"""
        return self._current_data

    def get_current_file(self) -> Optional[str]:
        """Get currently loaded file path"""
        return self._current_file
