"""Logging configuration for ML Data Pipeline Visualizer"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level=logging.INFO, log_to_file=True):
    """
    Set up application logging with both file and console handlers

    Args:
        log_level: Logging level (default: INFO)
        log_to_file: Whether to log to file (default: True)

    Returns:
        Logger instance
    """
    # Create logger
    logger = logging.getLogger('ml_visualizer')
    logger.setLevel(log_level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (DEBUG and above) - if enabled
    if log_to_file:
        try:
            # Create logs directory
            log_dir = Path.cwd() / 'logs'
            log_dir.mkdir(exist_ok=True)

            # Create log file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f'ml_visualizer_{timestamp}.log'

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)

            logger.info(f"Logging to file: {log_file}")

        except Exception as e:
            logger.warning(f"Could not set up file logging: {e}")

    return logger


def get_logger(name):
    """
    Get a logger instance for a specific module

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f'ml_visualizer.{name}')
