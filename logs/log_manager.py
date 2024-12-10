import logging
import os


class LogManager:
    def __init__(self, log_dir="logs"):
        """
        Initialize the LogManager.
        :param log_dir: Directory to store log files.
        """
        self.log_dir = log_dir
        self.scan_log_file = os.path.join(log_dir, "scan_log.txt")
        self.error_log_file = os.path.join(log_dir, "error_log.txt")
        self.activity_log_file = os.path.join(log_dir, "activity_log.txt")

        # Ensure the log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Configure logging
        self._setup_logging()

    def _setup_logging(self):
        """
        Configure logging for different log files.
        """
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.scan_log_file),
                logging.FileHandler(self.error_log_file),
                logging.FileHandler(self.activity_log_file),
                logging.StreamHandler()
            ]
        )

    def get_logger(self, name):
        """
        Get a logger instance with the specified name.
        :param name: Name of the logger.
        :return: Configured logger instance.
        """
        return logging.getLogger(name)


if __name__ == "__main__":
    # Example usage
    log_manager = LogManager()

    # Scan logger
    scan_logger = log_manager.get_logger("ScanLogger")
    scan_logger.info("Scan started.")
    scan_logger.info("Port 22 open.")
    scan_logger.info("Scan completed.")

    # Error logger
    error_logger = log_manager.get_logger("ErrorLogger")
    error_logger.error("Failed to connect to target.")

    # Activity logger
    activity_logger = log_manager.get_logger("ActivityLogger")
    activity_logger.info("User changed configuration.")
    activity_logger.info("Output directory set to reports/output.")
