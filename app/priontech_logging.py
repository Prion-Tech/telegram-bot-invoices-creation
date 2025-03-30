import logging
import sys
from typing import List, Optional, Union

from app.config import LOG_LEVEL, LOGGER_NAME

global_exclude_loggers = ()
# exclude_loggers = ['httpx']

class ExcludeLibraryFilter(logging.Filter):
    """
    Filter to exclude logs from specific libraries or modules.
    """

    def __init__(self, excluded_loggers: Union[List[str], str]):
        super().__init__()
        if isinstance(excluded_loggers, str):
            self.excluded_loggers = [excluded_loggers]
        else:
            self.excluded_loggers = excluded_loggers

    def filter(self, record):
        # Return False to exclude the record from logging
        for logger_name in self.excluded_loggers:
            if record.name.startswith(logger_name):
                return False
        return True


def setup_logging(exclude_loggers: List[str] = global_exclude_loggers) -> logging.Logger:
    """
    Set up and configure logger with console output.

    Args:
        exclude_loggers: List of logger names to exclude (e.g., ['httpx', 'urllib3'])

    Returns:
        A configured logger instance.
    """
    # Get logger instance
    logger = logging.getLogger(LOGGER_NAME)

    # Prevent adding handlers multiple times if setup_logging is called more than once
    if logger.handlers:
        return logger

    # Set log level
    logger.setLevel(LOG_LEVEL)

    # Create console handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(LOG_LEVEL)

    # Add filter to exclude specific loggers (like httpx)
    exclude_filter = ExcludeLibraryFilter(exclude_loggers)
    stdout_handler.addFilter(exclude_filter)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s - [%(message)s]')
    stdout_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(stdout_handler)

    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False

    return logger


def load_logger(name: Optional[str] = None, exclude_loggers: List[str] = global_exclude_loggers) -> logging.Logger:
    """
    Get an existing logger. If name is not provided, returns the main logger.
    If the main logger hasn't been set up yet, sets it up first.

    Args:
        name: Optional name for the logger, defaults to LOGGER_NAME from config
        exclude_loggers: List of logger names to exclude (e.g., ['httpx', 'urllib3'])

    Returns:
        Configured logger instance
    """
    logger_name = name if name else LOGGER_NAME

    # Get the logger
    logger = logging.getLogger(logger_name)

    # If this is the main logger and it has no handlers, set it up
    if logger_name == LOGGER_NAME and not logger.handlers:
        return setup_logging(exclude_loggers=exclude_loggers)

    return logger
