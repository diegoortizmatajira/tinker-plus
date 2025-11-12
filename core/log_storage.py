import logging
import os

from core.defaults import APP_LOG_FILE, APP_LOGS_DIR, PROTON_LOGS_DIR


class LogFactory:
    """
    Factory class to set up logging for the application.
    """

    def __init__(self, level=logging.INFO):
        logging.basicConfig(level=level)
        self.log_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
        )
        # Create log folders if they don't exist
        os.makedirs(APP_LOGS_DIR, exist_ok=True)
        os.makedirs(PROTON_LOGS_DIR, exist_ok=True)

        # Log to file
        self.file_handler = logging.FileHandler(APP_LOG_FILE)
        self.file_handler.setFormatter(self.log_formatter)
        self.file_handler.setLevel(level)
        # Log to terminal
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.log_formatter)
        self.console_handler.setLevel(level)

    def get_logger(self, name: str, level: int = logging.INFO) -> logging.Logger:
        """
        Returns a logger configured with file and console handlers.

        :param name: Name of the logger.
        :param level: Logging level.
        :return: Configured logger instance.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(self.file_handler)
        logger.addHandler(self.console_handler)
        return logger


logger_factory = LogFactory(logging.INFO)
