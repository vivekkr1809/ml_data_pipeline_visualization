"""Plotly widget for displaying interactive plots"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import plotly.graph_objects as go
import tempfile
import os
import sys
from src.core.logging_config import get_logger

logger = get_logger(__name__)


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
        logger.debug("PlotlyWidget initialized")
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
            logger.info("Generating Plotly figure HTML")
            logger.debug(f"Platform: {sys.platform}, Default encoding: {sys.getdefaultencoding()}")

            # Generate HTML from Plotly figure
            # Use include_plotlyjs=True to embed the library (works offline)
            html = figure.to_html(
                include_plotlyjs=True,
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

            html_size = len(html)
            logger.debug(f"Generated HTML size: {html_size / 1024:.2f} KB")

            # Clean up previous temp file
            if self._temp_file and os.path.exists(self._temp_file):
                try:
                    logger.debug(f"Cleaning up previous temp file: {self._temp_file}")
                    os.unlink(self._temp_file)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to clean up temp file: {cleanup_err}")

            # Create temporary file with UTF-8 encoding to handle Unicode characters
            logger.debug("Creating temporary HTML file with UTF-8 encoding")
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html)
                self._temp_file = f.name

            logger.info(f"Plotly HTML written to: {self._temp_file}")
            logger.debug(f"Temp file size: {os.path.getsize(self._temp_file) / 1024:.2f} KB")

            # Load in web view
            file_url = QUrl.fromLocalFile(self._temp_file)
            logger.debug(f"Loading URL in QWebEngineView: {file_url.toString()}")
            self._web_view.setUrl(file_url)

            logger.info("Successfully loaded Plotly figure")

        except UnicodeEncodeError as e:
            logger.error(f"Unicode encoding error: {e}", exc_info=True)
            logger.error(f"Platform: {sys.platform}, File encoding used: utf-8")
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
                    <h3>Unicode Encoding Error</h3>
                    <p>{str(e)}</p>
                    <p style="font-size: 12px; margin-top: 20px;">Check logs for details</p>
                </div>
            </body>
            </html>
            """
            self._web_view.setHtml(error_html)

        except Exception as e:
            logger.error(f"Unexpected error displaying Plotly figure: {e}", exc_info=True)
            logger.error(f"Figure type: {type(figure)}")
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
                    <p style="font-size: 12px; margin-top: 20px;">Check logs/ml_visualizer_*.log for details</p>
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
