"""Metrics display widget"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel,
                             QGroupBox, QFrame)
from PyQt6.QtCore import Qt
from typing import Optional
from src.core.interfaces.analyzer import AnalysisResult


class MetricsWidget(QWidget):
    """
    Widget for displaying analysis metrics
    Shows slope, R², RMSE, and other statistics
    """

    def __init__(self, parent=None):
        """Initialize metrics widget"""
        super().__init__(parent)
        self._metric_labels = {}
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()

        # Create group box
        group_box = QGroupBox("Linearity Metrics")
        group_layout = QGridLayout()

        # Define metrics to display
        metrics = [
            ('slope', 'Slope:', 0),
            ('intercept', 'Intercept:', 1),
            ('r2', 'R²:', 2),
            ('rmse', 'RMSE:', 3),
            ('pearson_r', 'Pearson r:', 4),
            ('p_value', 'P-value:', 5),
            ('n_points', 'Data Points:', 6),
        ]

        # Create labels for each metric
        for key, label_text, row in metrics:
            # Label
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("font-weight: bold;")

            # Value label
            value_label = QLabel("-")
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            value_label.setStyleSheet("font-family: monospace; color: #2E86AB;")

            # Add to layout
            group_layout.addWidget(label, row, 0)
            group_layout.addWidget(value_label, row, 1)

            # Store reference
            self._metric_labels[key] = value_label

        # Set column stretch
        group_layout.setColumnStretch(1, 1)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        layout.addStretch()

        self.setLayout(layout)

    def set_metrics(self, result: AnalysisResult):
        """
        Display metrics from analysis result

        Args:
            result: AnalysisResult containing metrics
        """
        # Update each metric
        for key, label in self._metric_labels.items():
            value = result.get_metric(key)

            if value is not None:
                # Format based on metric type
                if key == 'p_value':
                    # Scientific notation for p-value
                    formatted = f"{value:.4e}"
                elif key == 'n_points':
                    # Integer for count
                    formatted = f"{int(value)}"
                else:
                    # 6 decimal places for other metrics
                    formatted = f"{value:.6f}"

                label.setText(formatted)
            else:
                label.setText("-")

    def clear(self):
        """Clear all metrics"""
        for label in self._metric_labels.values():
            label.setText("-")
