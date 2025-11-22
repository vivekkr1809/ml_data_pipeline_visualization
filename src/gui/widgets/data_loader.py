"""Data loader widget for file selection and loading"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFileDialog, QMessageBox, QGroupBox)
from PyQt6.QtCore import pyqtSignal
import pandas as pd
from typing import Optional
from src.data.sources.csv_source import CSVDataSource


class DataLoaderWidget(QWidget):
    """
    Widget for loading CSV files
    Emits signal when data is successfully loaded
    """

    # Signal emitted when data is loaded (DataFrame, file_path)
    data_loaded = pyqtSignal(object, str)

    def __init__(self, parent=None):
        """Initialize data loader widget"""
        super().__init__(parent)
        self._data_source = CSVDataSource()
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

        self._load_button = QPushButton("Load CSV File")
        self._load_button.setToolTip("Select and load a CSV file")
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
        # Get supported extensions
        extensions = self._data_source.get_supported_extensions()
        filter_str = f"CSV Files (*{' *'.join(extensions)});;All Files (*.*)"

        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
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
            # Load data
            data = self._data_source.load(file_path)

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
