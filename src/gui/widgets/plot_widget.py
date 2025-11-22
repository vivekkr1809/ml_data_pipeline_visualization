"""Plot widget for displaying matplotlib figures"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from typing import Optional


class PlotWidget(QWidget):
    """
    Widget for displaying matplotlib plots with interactive toolbar
    Optimized for low latency and interactivity
    """

    def __init__(self, parent=None):
        """Initialize plot widget"""
        super().__init__(parent)
        self._figure: Optional[Figure] = None
        self._canvas: Optional[FigureCanvas] = None
        self._toolbar: Optional[NavigationToolbar] = None
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create initial empty figure
        self._figure = Figure(figsize=(8, 6), dpi=100)
        self._canvas = FigureCanvas(self._figure)

        # Configure canvas for better performance
        self._canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        # Create navigation toolbar for interactivity
        self._toolbar = NavigationToolbar(self._canvas, self)

        # Add to layout
        layout.addWidget(self._toolbar)
        layout.addWidget(self._canvas)

        self.setLayout(layout)

        # Initial empty plot
        self._show_empty_plot()

    def _show_empty_plot(self):
        """Show empty plot with instructions"""
        self._figure.clear()
        ax = self._figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Load CSV and select columns to generate plot',
               ha='center', va='center', fontsize=12, color='#999',
               transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        self._canvas.draw_idle()

    def set_figure(self, figure: Figure):
        """
        Set and display a new figure

        Args:
            figure: Matplotlib Figure to display
        """
        if self._canvas:
            # Remove old canvas
            layout = self.layout()
            layout.removeWidget(self._canvas)
            self._canvas.deleteLater()

        # Create new canvas with the figure
        self._figure = figure
        self._canvas = FigureCanvas(self._figure)
        self._canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        # Recreate toolbar
        if self._toolbar:
            layout = self.layout()
            layout.removeWidget(self._toolbar)
            self._toolbar.deleteLater()

        self._toolbar = NavigationToolbar(self._canvas, self)

        # Add to layout
        layout = self.layout()
        layout.insertWidget(0, self._toolbar)
        layout.insertWidget(1, self._canvas)

        # Draw
        self._canvas.draw()

    def clear(self):
        """Clear plot and show empty state"""
        self._show_empty_plot()

    def get_figure(self) -> Optional[Figure]:
        """Get current figure"""
        return self._figure
