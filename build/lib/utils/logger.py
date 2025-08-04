import logging
import sys
import os

def setup_logger(log_level=logging.INFO):
    """
    Sets up a comprehensive logger with different handlers for console and file.
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the lowest level to capture everything

    # Clear existing handlers to prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create console handler - shows INFO and higher
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create file handler for general activity - shows INFO and higher
    info_log_path = os.path.join(log_dir, "activity.log")
    info_handler = logging.FileHandler(info_log_path)
    info_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    info_handler.setFormatter(file_formatter)
    logger.addHandler(info_handler)
    
    # Create file handler for detailed debugging - shows DEBUG
