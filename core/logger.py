import logging
import os

def setup_logger(name: str, log_file: str, level: int = logging.INFO):
    """
    Set up a logger with the specified name, log file, and level.
    
    :param name: The name of the logger.
    :param log_file: Path to the log file where logs will be written.
    :param level: Logging level (e.g., logging.INFO, logging.DEBUG, logging.ERROR).
    """
    # Ensure the directory for the log file exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create a logger instance
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Create a console handler to print logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Define the log format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
