"""Main application entry point"""
import sys
import logging
from PyQt6.QtWidgets import QApplication
from src.core.logging_config import setup_logging, get_logger
from src.gui.main_window import MainWindow


def main():
    """
    Main application entry point
    Initializes and runs the ML Data Pipeline Visualizer
    """
    # Setup logging first
    setup_logging(log_level=logging.INFO, log_to_file=True)
    logger = get_logger(__name__)

    logger.info("="*60)
    logger.info("ML Data Pipeline Visualizer Starting")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info("="*60)

    # Create application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("ML Data Pipeline Visualizer")
    app.setOrganizationName("ML Data Pipeline")
    app.setApplicationVersion("0.2.0")
    logger.info("Application version: 0.2.0")

    # Set application style for better appearance on Windows
    app.setStyle("Fusion")
    logger.debug("Using Fusion style")

    try:
        # Create and show main window
        logger.info("Creating main window")
        main_window = MainWindow()
        main_window.show()
        logger.info("Main window displayed")

        # Run application event loop
        logger.info("Starting application event loop")
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Fatal error in main: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
