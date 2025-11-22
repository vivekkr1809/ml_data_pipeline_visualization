"""Main application window"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMessageBox, QStatusBar)
from PyQt6.QtCore import Qt
import pandas as pd
from typing import Optional

from src.gui.widgets.data_loader import DataLoaderWidget
from src.gui.widgets.column_selector import ColumnSelectorWidget
from src.gui.widgets.plot_widget import PlotWidget
from src.gui.widgets.metrics_widget import MetricsWidget
from src.analysis.correlation_analyzer import CorrelationAnalyzer
from src.visualization.renderers.correlation_renderer import CorrelationRenderer
from src.core.interfaces.renderer import RenderConfig


class MainWindow(QMainWindow):
    """
    Main application window
    Follows MVC pattern with clean separation of concerns
    """

    def __init__(self):
        """Initialize main window"""
        super().__init__()

        # Initialize components (Dependency Injection)
        self._analyzer = CorrelationAnalyzer()
        self._renderer = CorrelationRenderer()

        # Current state
        self._current_data: Optional[pd.DataFrame] = None
        self._current_x_col: Optional[str] = None
        self._current_y_col: Optional[str] = None

        # Initialize UI
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("ML Data Pipeline Visualizer - MVP")
        self.setMinimumSize(1200, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()

        # Left panel - Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5, 5, 5, 5)

        # Add widgets to left panel
        self._data_loader = DataLoaderWidget()
        self._column_selector = ColumnSelectorWidget()
        self._metrics_widget = MetricsWidget()

        left_layout.addWidget(self._data_loader)
        left_layout.addWidget(self._column_selector)
        left_layout.addWidget(self._metrics_widget)
        left_layout.addStretch()

        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(350)

        # Right panel - Plot
        self._plot_widget = PlotWidget()

        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self._plot_widget)
        splitter.setStretchFactor(0, 0)  # Left panel doesn't stretch
        splitter.setStretchFactor(1, 1)  # Plot stretches

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready - Load a CSV file to begin")

    def _connect_signals(self):
        """Connect widget signals to handlers"""
        # Data loaded signal
        self._data_loader.data_loaded.connect(self._on_data_loaded)

        # Columns selected signal
        self._column_selector.columns_selected.connect(self._on_columns_selected)

    def _on_data_loaded(self, data: pd.DataFrame, file_path: str):
        """
        Handle data loaded event

        Args:
            data: Loaded DataFrame
            file_path: Path to loaded file
        """
        self._current_data = data

        # Update column selector
        self._column_selector.set_data(data)

        # Clear previous results
        self._metrics_widget.clear()
        self._plot_widget.clear()

        # Update status
        file_name = file_path.split('/')[-1].split('\\')[-1]
        self._status_bar.showMessage(f"Loaded: {file_name} - Select columns and generate plot")

    def _on_columns_selected(self, x_col: str, y_col: str):
        """
        Handle column selection and generate plot

        Args:
            x_col: X column name
            y_col: Y column name
        """
        if self._current_data is None:
            QMessageBox.warning(self, "No Data", "Please load a CSV file first")
            return

        self._current_x_col = x_col
        self._current_y_col = y_col

        try:
            # Update status
            self._status_bar.showMessage("Analyzing data...")

            # Perform analysis
            analysis_result = self._analyzer.analyze(
                self._current_data,
                column_x=x_col,
                column_y=y_col
            )

            # Update metrics display
            self._metrics_widget.set_metrics(analysis_result)

            # Create render configuration
            config = RenderConfig(
                title=f"Correlation Analysis: {x_col} vs {y_col}",
                xlabel=x_col,
                ylabel=y_col,
                interactive=True
            )

            # Render plot with metrics
            figure = self._renderer.render_with_metrics(
                self._current_data,
                config,
                analysis_result,
                column_x=x_col,
                column_y=y_col
            )

            # Display plot
            self._plot_widget.set_figure(figure)

            # Update status
            r2 = analysis_result.get_metric('r2')
            self._status_bar.showMessage(
                f"Plot generated - {x_col} vs {y_col} (R² = {r2:.4f})"
            )

        except Exception as e:
            # Show error
            QMessageBox.critical(
                self,
                "Analysis Error",
                f"Failed to generate plot:\n{str(e)}"
            )
            self._status_bar.showMessage("Error generating plot")
