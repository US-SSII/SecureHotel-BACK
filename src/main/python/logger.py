import os
from datetime import datetime

from loguru import logger


def load_logger() -> None:
    """
    Initializes the Logger.

    Args:
        is_test (bool, optional): Indicates if the logger is used for testing purposes.
    """
    # Get the current date or use a specific date for tests
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Create a file name with the date
    log_file_name = f'{current_date}_log.txt'
    log_file_path = os.path.join(
        '../logs/', log_file_name)

    # Configure the Loguru logger
    fmt = "{level} - {time} - {message}"
    logger.add(log_file_path, rotation="1 day", format=fmt, level="ERROR")
    logger.add(log_file_path, rotation="1 day", format=fmt, level="SUCCESS")
    logger.add(log_file_path, rotation="1 day", format=fmt, level="INFO")

