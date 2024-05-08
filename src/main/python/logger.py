import os
from datetime import datetime

from loguru import logger


def load_logger(is_test: bool = False) -> None:
    """
    Initializes the Logger.

    Args:
        is_test (bool, optional): Indicates if the logger is used for testing purposes.
    """
    # Get the current date or use a specific date for tests
    current_date = datetime.now().strftime('%Y-%m-%d')

    if is_test:
        current_date = '9999-99-99'
        try:
            with open("../traffic_capture/9999-99-99_log.txt", 'r+') as archivo:
                archivo.seek(0)
                archivo.truncate()
        except FileNotFoundError:
            pass

    # Create a file name with the date
    log_file_name = f'{current_date}_log.txt'
    log_file_path = os.path.join(
        '../traffic_capture/', log_file_name)

    # Configure the Loguru logger
    fmt = "{level} - {time} - {message}"
    logger.add(log_file_path, rotation="1 day", format=fmt, level="ERROR")
    logger.add(log_file_path, rotation="1 day", format=fmt, level="SUCCESS")
    logger.add(log_file_path, rotation="1 day", format=fmt, level="INFO")

