#!/usr/bin/env python3
"""
Centralized logging system for Eastbound automation.

Usage:
    from logger import get_logger, setup_logging

    # At the start of your script:
    setup_logging(log_file='logs/automation.log', verbose=True)
    logger = get_logger(__name__)

    # In your code:
    logger.info("Processing started")
    logger.error("Something failed", exc_info=True)
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Global logger configuration
_configured = False

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # Add color to level name for console
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        return super().format(record)


def setup_logging(log_file=None, verbose=False, console_level=None):
    """
    Set up logging configuration.

    Args:
        log_file: Path to log file (relative to project root or absolute)
        verbose: If True, set console to DEBUG level
        console_level: Override console logging level (DEBUG, INFO, WARNING, ERROR)
    """
    global _configured

    if _configured:
        return  # Already configured

    # Determine log file path
    if log_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = LOGS_DIR / f'automation_{timestamp}.log'
    elif not Path(log_file).is_absolute():
        log_file = Path(__file__).parent.parent / log_file
    else:
        log_file = Path(log_file)

    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything

    # Remove existing handlers
    root_logger.handlers.clear()

    # File handler - always DEBUG level, captures everything
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console handler - configurable level
    console_handler = logging.StreamHandler(sys.stdout)
    if console_level:
        console_handler.setLevel(getattr(logging, console_level.upper()))
    elif verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)

    console_formatter = ColoredFormatter(
        '[%(levelname)s] %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Log the logging setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized: {log_file}")
    logger.debug(f"Console level: {console_handler.level} | File level: DEBUG")

    _configured = True

    return log_file


def get_logger(name):
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger instance
    """
    return logging.getLogger(name)


# Convenience function for scripts
def init_script_logging(script_name, verbose=False):
    """
    Initialize logging for a standalone script.

    Args:
        script_name: Name of the script (e.g., 'monitor_russian_media')
        verbose: Enable verbose (DEBUG) logging to console

    Returns:
        Logger instance and log file path
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = LOGS_DIR / f'{script_name}_{timestamp}.log'

    setup_logging(log_file=log_file, verbose=verbose)
    logger = get_logger(script_name)

    return logger, log_file


if __name__ == '__main__':
    # Test the logging system
    setup_logging(verbose=True)
    logger = get_logger('test')

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    try:
        1 / 0
    except Exception as e:
        logger.error("Caught an exception", exc_info=True)

    print(f"\nLog files are stored in: {LOGS_DIR}")
