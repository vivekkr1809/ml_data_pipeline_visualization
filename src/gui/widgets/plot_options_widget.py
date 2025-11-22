"""Plot options widget for selecting plot type and rendering mode"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QRadioButton, QButtonGroup, QGroupBox)
from PyQt6.QtCore import pyqtSignal


class PlotOptionsWidget(QWidget):
    """
    Widget for selecting plot type and rendering mode
    """

    # Signals emitted when options change
    plot_type_changed = pyqtSignal(str)  # 'correlation', 'contour', 'pca', or 'tsne'
    mode_changed = pyqtSignal(str)  # 'static' or 'interactive'

    def __init__(self, parent=None):
        """Initialize plot options widget"""
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()

        # Create group box
        group_box = QGroupBox("Plot Options")
        group_layout = QVBoxLayout()

        # Plot type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Plot Type:")
        type_label.setFixedWidth(80)

        self._type_combo = QComboBox()
        self._type_combo.addItems(["Correlation", "Contour", "PCA Latent Space", "t-SNE Latent Space"])
        self._type_combo.setToolTip("Select the type of plot to generate")
        self._type_combo.currentTextChanged.connect(self._on_type_changed)

        type_layout.addWidget(type_label)
        type_layout.addWidget(self._type_combo)

        # Rendering mode selection
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("font-weight: bold; margin-top: 10px;")

        # Radio buttons for mode
        self._static_radio = QRadioButton("Static (Matplotlib)")
        self._static_radio.setToolTip("Static plots with Matplotlib")
        self._static_radio.setChecked(True)  # Default to static

        self._interactive_radio = QRadioButton("Interactive (Plotly)")
        self._interactive_radio.setToolTip("Interactive plots with Plotly")

        # Button group for exclusive selection
        self._mode_group = QButtonGroup()
        self._mode_group.addButton(self._static_radio)
        self._mode_group.addButton(self._interactive_radio)
        self._mode_group.buttonClicked.connect(self._on_mode_changed)

        # Add to group layout
        group_layout.addLayout(type_layout)
        group_layout.addWidget(mode_label)
        group_layout.addWidget(self._static_radio)
        group_layout.addWidget(self._interactive_radio)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        self.setLayout(layout)

    def _on_type_changed(self, text):
        """Handle plot type change"""
        type_map = {
            'Correlation': 'correlation',
            'Contour': 'contour',
            'PCA Latent Space': 'pca',
            't-SNE Latent Space': 'tsne'
        }
        plot_type = type_map.get(text, 'correlation')
        self.plot_type_changed.emit(plot_type)

    def _on_mode_changed(self):
        """Handle mode change"""
        mode = 'interactive' if self._interactive_radio.isChecked() else 'static'
        self.mode_changed.emit(mode)

    def get_plot_type(self) -> str:
        """
        Get currently selected plot type

        Returns:
            'correlation', 'contour', 'pca', or 'tsne'
        """
        type_map = {
            'Correlation': 'correlation',
            'Contour': 'contour',
            'PCA Latent Space': 'pca',
            't-SNE Latent Space': 'tsne'
        }
        return type_map.get(self._type_combo.currentText(), 'correlation')

    def get_mode(self) -> str:
        """
        Get currently selected rendering mode

        Returns:
            'static' or 'interactive'
        """
        return 'interactive' if self._interactive_radio.isChecked() else 'static'

    def set_plot_type(self, plot_type: str):
        """Set plot type programmatically"""
        index_map = {
            'correlation': 0,
            'contour': 1,
            'pca': 2,
            'tsne': 3
        }
        index = index_map.get(plot_type, 0)
        self._type_combo.setCurrentIndex(index)

    def set_mode(self, mode: str):
        """Set rendering mode programmatically"""
        if mode == 'interactive':
            self._interactive_radio.setChecked(True)
        else:
            self._static_radio.setChecked(True)
