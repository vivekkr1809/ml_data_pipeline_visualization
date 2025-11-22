"""Plotly widget for displaying interactive plots"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import plotly.graph_objects as go
import tempfile
import os


class PlotlyWidget(QWidget):
    """
    Widget for displaying Plotly interactive plots
    Uses QWebEngineView to render Plotly HTML
    """

    def __init__(self, parent=None):
        """Initialize Plotly widget"""
        super().__init__(parent)
        self._web_view = None
        self._temp_file = None
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create web view for interactive plots
        self._web_view = QWebEngineView()
        self._web_view.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        layout.addWidget(self._web_view)
        self.setLayout(layout)

        # Show empty state initially
        self._show_empty_plot()

    def _show_empty_plot(self):
        """Show empty plot with instructions"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                }
                .message {
                    text-align: center;
                    color: #999;
                    font-size: 16px;
                }
            </style>
        </head>
        <body>
            <div class="message">
                Load CSV and select columns to generate interactive plot
            </div>
        </body>
        </html>
        """
        self._web_view.setHtml(html)

    def set_figure(self, figure: go.Figure):
        """
        Set and display a Plotly figure

        Args:
            figure: Plotly Figure to display
        """
        try:
            # Generate HTML from Plotly figure
            html = figure.to_html(
                include_plotlyjs='cdn',
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['sendDataToCloud'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'plot',
                        'height': 800,
                        'width': 1200,
                        'scale': 2
                    }
                }
            )

            # Clean up previous temp file
            if self._temp_file and os.path.exists(self._temp_file):
                try:
                    os.unlink(self._temp_file)
                except:
                    pass

            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html)
                self._temp_file = f.name

            # Load in web view
            self._web_view.setUrl(QUrl.fromLocalFile(self._temp_file))

        except Exception as e:
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        font-family: Arial, sans-serif;
                        background-color: #f5f5f5;
                    }}
                    .error {{
                        text-align: center;
                        color: #d32f2f;
                        font-size: 14px;
                        padding: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h3>Error displaying plot</h3>
                    <p>{str(e)}</p>
                </div>
            </body>
            </html>
            """
            self._web_view.setHtml(error_html)

    def clear(self):
        """Clear plot and show empty state"""
        self._show_empty_plot()

        # Clean up temp file
        if self._temp_file and os.path.exists(self._temp_file):
            try:
                os.unlink(self._temp_file)
                self._temp_file = None
            except:
                pass

    def __del__(self):
        """Clean up temporary file on deletion"""
        if self._temp_file and os.path.exists(self._temp_file):
            try:
                os.unlink(self._temp_file)
            except:
                pass
