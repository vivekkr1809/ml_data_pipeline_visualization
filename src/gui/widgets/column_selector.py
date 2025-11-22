"""Column selector widget for choosing X, Y, and Z columns"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLabel, QPushButton, QGroupBox)
from PyQt6.QtCore import pyqtSignal
import pandas as pd
from typing import Optional


class ColumnSelectorWidget(QWidget):
    """
    Widget for selecting X, Y, and optionally Z columns from loaded data
    Emits signal when valid selection is made
    """

    # Signal emitted when columns are selected (x_column, y_column, z_column)
    columns_selected = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        """Initialize column selector widget"""
        super().__init__(parent)
        self._current_data = None
        self._plot_type = 'correlation'  # 'correlation' or 'contour'
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()

        # Create group box
        group_box = QGroupBox("Column Selection")
        group_layout = QVBoxLayout()

        # X column selection
        x_layout = QHBoxLayout()
        x_label = QLabel("X Column:")
        x_label.setFixedWidth(80)
        self._x_combo = QComboBox()
        self._x_combo.setToolTip("Select column for X-axis")
        self._x_combo.currentTextChanged.connect(self._on_selection_changed)
        x_layout.addWidget(x_label)
        x_layout.addWidget(self._x_combo)

        # Y column selection
        y_layout = QHBoxLayout()
        y_label = QLabel("Y Column:")
        y_label.setFixedWidth(80)
        self._y_combo = QComboBox()
        self._y_combo.setToolTip("Select column for Y-axis")
        self._y_combo.currentTextChanged.connect(self._on_selection_changed)
        y_layout.addWidget(y_label)
        y_layout.addWidget(self._y_combo)

        # Z column selection (for contour plots)
        self._z_layout = QHBoxLayout()
        self._z_label = QLabel("Z Column:")
        self._z_label.setFixedWidth(80)
        self._z_combo = QComboBox()
        self._z_combo.setToolTip("Select column for Z-axis (contour plots)")
        self._z_combo.currentTextChanged.connect(self._on_selection_changed)
        self._z_layout.addWidget(self._z_label)
        self._z_layout.addWidget(self._z_combo)

        # Create container widget for Z column (for showing/hiding)
        self._z_widget = QWidget()
        self._z_widget.setLayout(self._z_layout)
        self._z_widget.setVisible(False)  # Hidden by default for correlation

        # Plot button
        self._plot_button = QPushButton("Generate Plot")
        self._plot_button.setEnabled(False)
        self._plot_button.setToolTip("Generate plot")
        self._plot_button.clicked.connect(self._on_plot_clicked)

        # Add to group layout
        group_layout.addLayout(x_layout)
        group_layout.addLayout(y_layout)
        group_layout.addWidget(self._z_widget)
        group_layout.addWidget(self._plot_button)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        self.setLayout(layout)

        # Initially disabled
        self._set_enabled(False)

    def set_data(self, data: pd.DataFrame):
        """
        Set data and populate column dropdowns

        Args:
            data: DataFrame to extract columns from
        """
        self._current_data = data

        # Get numeric columns only
        numeric_columns = data.select_dtypes(include=['number']).columns.tolist()

        # Clear and populate dropdowns
        self._x_combo.clear()
        self._y_combo.clear()
        self._z_combo.clear()

        if numeric_columns:
            self._x_combo.addItems(numeric_columns)
            self._y_combo.addItems(numeric_columns)
            self._z_combo.addItems(numeric_columns)

            # Auto-select columns based on plot type
            if self._plot_type == 'contour':
                # For contour: select first 3 columns
                if len(numeric_columns) >= 3:
                    self._x_combo.setCurrentIndex(0)
                    self._y_combo.setCurrentIndex(1)
                    self._z_combo.setCurrentIndex(2)
                elif len(numeric_columns) >= 2:
                    self._x_combo.setCurrentIndex(0)
                    self._y_combo.setCurrentIndex(1)
                    self._z_combo.setCurrentIndex(0)
                elif len(numeric_columns) == 1:
                    self._x_combo.setCurrentIndex(0)
                    self._y_combo.setCurrentIndex(0)
                    self._z_combo.setCurrentIndex(0)
            else:
                # For correlation: select first 2 columns
                if len(numeric_columns) >= 2:
                    self._x_combo.setCurrentIndex(0)
                    self._y_combo.setCurrentIndex(1)
                elif len(numeric_columns) == 1:
                    self._x_combo.setCurrentIndex(0)
                    self._y_combo.setCurrentIndex(0)

            self._set_enabled(True)
        else:
            self._set_enabled(False)

    def _set_enabled(self, enabled: bool):
        """Enable or disable widget"""
        self._x_combo.setEnabled(enabled)
        self._y_combo.setEnabled(enabled)
        self._z_combo.setEnabled(enabled)
        self._plot_button.setEnabled(enabled)

    def _on_selection_changed(self):
        """Handle selection change"""
        # Enable plot button based on required columns
        x_col = self._x_combo.currentText()
        y_col = self._y_combo.currentText()

        if self._plot_type == 'contour':
            z_col = self._z_combo.currentText()
            self._plot_button.setEnabled(bool(x_col and y_col and z_col))
        else:
            self._plot_button.setEnabled(bool(x_col and y_col))

    def _on_plot_clicked(self):
        """Handle plot button click"""
        x_col = self._x_combo.currentText()
        y_col = self._y_combo.currentText()
        z_col = self._z_combo.currentText() if self._plot_type == 'contour' else ''

        if self._plot_type == 'contour':
            if x_col and y_col and z_col:
                self.columns_selected.emit(x_col, y_col, z_col)
        else:
            if x_col and y_col:
                self.columns_selected.emit(x_col, y_col, '')

    def set_plot_type(self, plot_type: str):
        """
        Set plot type and adjust UI accordingly

        Args:
            plot_type: 'correlation' or 'contour'
        """
        self._plot_type = plot_type
        self._z_widget.setVisible(plot_type == 'contour')

        # Re-populate if data is available
        if self._current_data is not None:
            self.set_data(self._current_data)

    def get_selected_columns(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Get currently selected columns

        Returns:
            Tuple of (x_column, y_column, z_column)
            z_column will be None for correlation plots
        """
        x_col = self._x_combo.currentText()
        y_col = self._y_combo.currentText()
        z_col = self._z_combo.currentText() if self._plot_type == 'contour' else None
        return (x_col if x_col else None,
                y_col if y_col else None,
                z_col if z_col else None)

    def clear(self):
        """Clear selections"""
        self._x_combo.clear()
        self._y_combo.clear()
        self._z_combo.clear()
        self._current_data = None
        self._set_enabled(False)
