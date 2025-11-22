"""Latent space feature selector widget for PCA and t-SNE"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLabel, QPushButton, QGroupBox, QCheckBox,
                             QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import pyqtSignal
import pandas as pd
from typing import Optional, List


class LatentSpaceSelectorWidget(QWidget):
    """
    Widget for selecting features and parameters for latent space visualization
    Supports both PCA and t-SNE
    """

    # Signal emitted when analysis parameters are set (plot_type, params_dict)
    analysis_requested = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        """Initialize latent space selector widget"""
        super().__init__(parent)
        self._current_data = None
        self._plot_type = 'pca'  # 'pca' or 'tsne'
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()

        # Create group box
        group_box = QGroupBox("Latent Space Analysis")
        group_layout = QVBoxLayout()

        # Feature selection
        feature_label = QLabel("<b>Feature Selection:</b>")
        group_layout.addWidget(feature_label)

        # Use all numeric columns checkbox
        self._use_all_features = QCheckBox("Use all numeric columns as features")
        self._use_all_features.setChecked(True)
        self._use_all_features.setToolTip("Automatically use all numeric columns (except target)")
        self._use_all_features.stateChanged.connect(self._on_use_all_changed)
        group_layout.addWidget(self._use_all_features)

        # Target column selection (optional, for coloring)
        target_layout = QHBoxLayout()
        target_label = QLabel("Target Column:")
        target_label.setFixedWidth(120)
        target_label.setToolTip("Optional column for coloring points")

        self._target_combo = QComboBox()
        self._target_combo.setToolTip("Select column for coloring (optional)")
        self._target_combo.addItem("(None)")

        target_layout.addWidget(target_label)
        target_layout.addWidget(self._target_combo)
        group_layout.addLayout(target_layout)

        # Components selection
        comp_layout = QHBoxLayout()
        comp_label = QLabel("Components:")
        comp_label.setFixedWidth(120)
        comp_label.setToolTip("Number of output dimensions (2 or 3)")

        self._components_spin = QSpinBox()
        self._components_spin.setRange(2, 3)
        self._components_spin.setValue(2)
        self._components_spin.setToolTip("2D or 3D visualization")

        comp_layout.addWidget(comp_label)
        comp_layout.addWidget(self._components_spin)
        comp_layout.addStretch()
        group_layout.addLayout(comp_layout)

        # t-SNE specific parameters (hidden for PCA)
        self._tsne_params_widget = QWidget()
        tsne_layout = QVBoxLayout()
        tsne_layout.setContentsMargins(0, 0, 0, 0)

        tsne_label = QLabel("<b>t-SNE Parameters:</b>")
        tsne_layout.addWidget(tsne_label)

        # Perplexity
        perp_layout = QHBoxLayout()
        perp_label = QLabel("Perplexity:")
        perp_label.setFixedWidth(120)
        perp_label.setToolTip("Balances local vs global structure (5-50)")

        self._perplexity_spin = QSpinBox()
        self._perplexity_spin.setRange(5, 100)
        self._perplexity_spin.setValue(30)
        self._perplexity_spin.setToolTip("Higher = more global structure")

        perp_layout.addWidget(perp_label)
        perp_layout.addWidget(self._perplexity_spin)
        perp_layout.addStretch()
        tsne_layout.addLayout(perp_layout)

        # Learning rate
        lr_layout = QHBoxLayout()
        lr_label = QLabel("Learning Rate:")
        lr_label.setFixedWidth(120)
        lr_label.setToolTip("Optimization learning rate (10-1000)")

        self._learning_rate_spin = QDoubleSpinBox()
        self._learning_rate_spin.setRange(10, 1000)
        self._learning_rate_spin.setValue(200)
        self._learning_rate_spin.setDecimals(0)
        self._learning_rate_spin.setToolTip("Higher = larger steps")

        lr_layout.addWidget(lr_label)
        lr_layout.addWidget(self._learning_rate_spin)
        lr_layout.addStretch()
        tsne_layout.addLayout(lr_layout)

        # Iterations
        iter_layout = QHBoxLayout()
        iter_label = QLabel("Iterations:")
        iter_label.setFixedWidth(120)
        iter_label.setToolTip("Number of optimization iterations")

        self._iterations_spin = QSpinBox()
        self._iterations_spin.setRange(250, 5000)
        self._iterations_spin.setValue(1000)
        self._iterations_spin.setSingleStep(250)
        self._iterations_spin.setToolTip("More = better convergence")

        iter_layout.addWidget(iter_label)
        iter_layout.addWidget(self._iterations_spin)
        iter_layout.addStretch()
        tsne_layout.addLayout(iter_layout)

        self._tsne_params_widget.setLayout(tsne_layout)
        self._tsne_params_widget.setVisible(False)  # Hidden by default for PCA
        group_layout.addWidget(self._tsne_params_widget)

        # Standardize features checkbox
        self._standardize_check = QCheckBox("Standardize features (recommended)")
        self._standardize_check.setChecked(True)
        self._standardize_check.setToolTip("Apply StandardScaler before analysis")
        group_layout.addWidget(self._standardize_check)

        # Analyze button
        self._analyze_button = QPushButton("Generate Latent Space Plot")
        self._analyze_button.setEnabled(False)
        self._analyze_button.setToolTip("Run analysis and generate plot")
        self._analyze_button.clicked.connect(self._on_analyze_clicked)
        group_layout.addWidget(self._analyze_button)

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

        # Get all columns and numeric columns
        all_columns = data.columns.tolist()
        numeric_columns = data.select_dtypes(include=['number']).columns.tolist()

        # Clear and populate target combo (can be any column)
        self._target_combo.clear()
        self._target_combo.addItem("(None)")
        if all_columns:
            self._target_combo.addItems(all_columns)

        # Enable if we have enough numeric columns
        if len(numeric_columns) >= 2:
            self._set_enabled(True)
        else:
            self._set_enabled(False)

    def _set_enabled(self, enabled: bool):
        """Enable or disable widget"""
        self._use_all_features.setEnabled(enabled)
        self._target_combo.setEnabled(enabled)
        self._components_spin.setEnabled(enabled)
        self._perplexity_spin.setEnabled(enabled)
        self._learning_rate_spin.setEnabled(enabled)
        self._iterations_spin.setEnabled(enabled)
        self._standardize_check.setEnabled(enabled)
        self._analyze_button.setEnabled(enabled)

    def _on_use_all_changed(self, state):
        """Handle use all features checkbox change"""
        # Currently we only support "use all", but could add manual selection later
        pass

    def _on_analyze_clicked(self):
        """Handle analyze button click"""
        if self._current_data is None:
            return

        # Gather parameters
        params = {
            'n_components': self._components_spin.value(),
            'standardize': self._standardize_check.isChecked(),
            'random_state': 42
        }

        # Add target column if selected
        target_text = self._target_combo.currentText()
        if target_text != "(None)":
            params['target_column'] = target_text

        # Add t-SNE specific parameters
        if self._plot_type == 'tsne':
            params['perplexity'] = self._perplexity_spin.value()
            params['learning_rate'] = self._learning_rate_spin.value()
            params['n_iter'] = self._iterations_spin.value()

        # Emit signal
        self.analysis_requested.emit(self._plot_type, params)

    def set_plot_type(self, plot_type: str):
        """
        Set plot type and adjust UI accordingly

        Args:
            plot_type: 'pca' or 'tsne'
        """
        self._plot_type = plot_type
        self._tsne_params_widget.setVisible(plot_type == 'tsne')

        # Update button text
        if plot_type == 'pca':
            self._analyze_button.setText("Generate PCA Plot")
        else:
            self._analyze_button.setText("Generate t-SNE Plot")

    def clear(self):
        """Clear selections"""
        self._target_combo.clear()
        self._target_combo.addItem("(None)")
        self._current_data = None
        self._set_enabled(False)
