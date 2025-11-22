"""Main application entry point"""
import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def main():
    """
    Main application entry point
    Initializes and runs the ML Data Pipeline Visualizer
    """
    # Create application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("ML Data Pipeline Visualizer")
    app.setOrganizationName("ML Data Pipeline")
    app.setApplicationVersion("0.1.0")

    # Set application style for better appearance on Windows
    app.setStyle("Fusion")

    # Create and show main window
    main_window = MainWindow()
    main_window.show()

    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
