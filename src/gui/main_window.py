"""Main application window with contour and interactive plot support"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMessageBox, QStatusBar, QStackedWidget)
from PyQt6.QtCore import Qt
import pandas as pd
from typing import Optional

from src.gui.widgets.data_loader import DataLoaderWidget
from src.gui.widgets.column_selector import ColumnSelectorWidget
from src.gui.widgets.plot_widget import PlotWidget
from src.gui.widgets.plotly_widget import PlotlyWidget
from src.gui.widgets.metrics_widget import MetricsWidget
from src.gui.widgets.plot_options_widget import PlotOptionsWidget

from src.analysis.correlation_analyzer import CorrelationAnalyzer
from src.analysis.contour_analyzer import ContourAnalyzer

from src.visualization.renderers.correlation_renderer import CorrelationRenderer
from src.visualization.renderers.contour_renderer import ContourRenderer
from src.visualization.renderers.plotly_correlation_renderer import PlotlyCorrelationRenderer
from src.visualization.renderers.plotly_contour_renderer import PlotlyContourRenderer

from src.core.interfaces.renderer import RenderConfig


class MainWindow(QMainWindow):
    """
    Main application window with support for multiple plot types and rendering modes
    Follows MVC pattern with clean separation of concerns
    """

    def __init__(self):
        """Initialize main window"""
        super().__init__()

        # Initialize analyzers
        self._correlation_analyzer = CorrelationAnalyzer()
        self._contour_analyzer = ContourAnalyzer()

        # Initialize renderers
        self._correlation_renderer = CorrelationRenderer()
        self._contour_renderer = ContourRenderer()
        self._plotly_correlation_renderer = PlotlyCorrelationRenderer()
        self._plotly_contour_renderer = PlotlyContourRenderer()

        # Current state
        self._current_data: Optional[pd.DataFrame] = None
        self._current_plot_type = 'correlation'
        self._current_mode = 'static'

        # Initialize UI
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("ML Data Pipeline Visualizer - Interactive & Contour Support")
        self.setMinimumSize(1300, 800)

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
        self._plot_options = PlotOptionsWidget()
        self._column_selector = ColumnSelectorWidget()
        self._metrics_widget = MetricsWidget()

        left_layout.addWidget(self._data_loader)
        left_layout.addWidget(self._plot_options)
        left_layout.addWidget(self._column_selector)
        left_layout.addWidget(self._metrics_widget)
        left_layout.addStretch()

        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(380)

        # Right panel - Plot display (stacked for matplotlib/plotly)
        self._plot_stack = QStackedWidget()

        # Add both plot widgets
        self._matplotlib_plot = PlotWidget()
        self._plotly_plot = PlotlyWidget()

        self._plot_stack.addWidget(self._matplotlib_plot)  # Index 0
        self._plot_stack.addWidget(self._plotly_plot)      # Index 1

        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self._plot_stack)
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

        # Plot options changed
        self._plot_options.plot_type_changed.connect(self._on_plot_type_changed)
        self._plot_options.mode_changed.connect(self._on_mode_changed)

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
        self._matplotlib_plot.clear()
        self._plotly_plot.clear()

        # Update status
        file_name = file_path.split('/')[-1].split('\\')[-1]
        self._status_bar.showMessage(f"Loaded: {file_name} - Select plot type and columns")

    def _on_plot_type_changed(self, plot_type: str):
        """
        Handle plot type change

        Args:
            plot_type: 'correlation' or 'contour'
        """
        self._current_plot_type = plot_type
        self._column_selector.set_plot_type(plot_type)
        self._status_bar.showMessage(f"Plot type: {plot_type.capitalize()}")

    def _on_mode_changed(self, mode: str):
        """
        Handle rendering mode change

        Args:
            mode: 'static' or 'interactive'
        """
        self._current_mode = mode

        # Switch plot widget
        if mode == 'interactive':
            self._plot_stack.setCurrentIndex(1)  # Plotly
        else:
            self._plot_stack.setCurrentIndex(0)  # Matplotlib

        self._status_bar.showMessage(f"Rendering mode: {mode.capitalize()}")

    def _on_columns_selected(self, x_col: str, y_col: str, z_col: str):
        """
        Handle column selection and generate plot

        Args:
            x_col: X column name
            y_col: Y column name
            z_col: Z column name (empty for correlation)
        """
        if self._current_data is None:
            QMessageBox.warning(self, "No Data", "Please load a CSV file first")
            return

        try:
            # Update status
            self._status_bar.showMessage("Generating plot...")

            if self._current_plot_type == 'correlation':
                self._generate_correlation_plot(x_col, y_col)
            else:  # contour
                self._generate_contour_plot(x_col, y_col, z_col)

        except Exception as e:
            # Show error
            QMessageBox.critical(
                self,
                "Plot Error",
                f"Failed to generate plot:\n{str(e)}"
            )
            self._status_bar.showMessage("Error generating plot")

    def _generate_correlation_plot(self, x_col: str, y_col: str):
        """Generate correlation plot"""
        # Perform analysis
        analysis_result = self._correlation_analyzer.analyze(
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
            interactive=(self._current_mode == 'interactive')
        )

        # Render plot based on mode
        if self._current_mode == 'interactive':
            # Use Plotly renderer
            figure = self._plotly_correlation_renderer.render_with_metrics(
                self._current_data,
                config,
                analysis_result,
                column_x=x_col,
                column_y=y_col
            )
            self._plotly_plot.set_figure(figure)
        else:
            # Use Matplotlib renderer
            figure = self._correlation_renderer.render_with_metrics(
                self._current_data,
                config,
                analysis_result,
                column_x=x_col,
                column_y=y_col
            )
            self._matplotlib_plot.set_figure(figure)

        # Update status
        r2 = analysis_result.get_metric('r2')
        self._status_bar.showMessage(
            f"Correlation plot generated - {x_col} vs {y_col} (R² = {r2:.4f})"
        )

    def _generate_contour_plot(self, x_col: str, y_col: str, z_col: str):
        """Generate contour plot"""
        # Perform analysis
        analysis_result = self._contour_analyzer.analyze(
            self._current_data,
            column_x=x_col,
            column_y=y_col,
            column_z=z_col
        )

        # Update metrics display (contour uses different metrics)
        # Note: metrics_widget needs updating to handle contour metrics
        # For now, we'll just clear it or skip
        self._metrics_widget.clear()

        # Create render configuration
        config = RenderConfig(
            title=f"Contour Plot: {z_col}",
            xlabel=x_col,
            ylabel=y_col,
            interactive=(self._current_mode == 'interactive')
        )

        # Render plot based on mode
        if self._current_mode == 'interactive':
            # Use Plotly renderer
            figure = self._plotly_contour_renderer.render_with_metrics(
                self._current_data,
                config,
                analysis_result,
                column_x=x_col,
                column_y=y_col,
                column_z=z_col
            )
            self._plotly_plot.set_figure(figure)
        else:
            # Use Matplotlib renderer
            figure = self._contour_renderer.render_with_metrics(
                self._current_data,
                config,
                analysis_result,
                column_x=x_col,
                column_y=y_col,
                column_z=z_col
            )
            self._matplotlib_plot.set_figure(figure)

        # Update status
        z_range = analysis_result.get_metric('z_range')
        self._status_bar.showMessage(
            f"Contour plot generated - {z_col} (Range = {z_range:.2f})"
        )
