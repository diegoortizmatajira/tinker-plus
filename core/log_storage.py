"""Module to set up logging for the application."""

import logging
import os
from typing import Optional

from core.defaults import APP_LOG_FILE


class LogFactory:
    """
    Factory class to set up logging for the application.
    """

    _instance: Optional["LogFactory"] = None

    def __init__(self, level=logging.DEBUG, file_output: bool = False):
        logging.basicConfig(
            level=level, format="%(levelname)s - [%(name)s] - %(message)s"
        )

        self.file_handler: Optional[logging.FileHandler] = None
        if file_output:
            if os.path.exists(APP_LOG_FILE):
                os.remove(APP_LOG_FILE)
            # Log to file
            self.file_handler = logging.FileHandler(APP_LOG_FILE)
            self.file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
                )
            )
            self.file_handler.setLevel(level)

    def get_logger(self, name: str) -> logging.Logger:
        """
        Returns a logger configured with file and console handlers.

        :param name: Name of the logger.
        :param level: Logging level.
        :return: Configured logger instance.
        """
        logger = logging.getLogger(name)
        if self.file_handler:
            logger.addHandler(self.file_handler)
        return logger

    @classmethod
    def initialize(cls, level=logging.DEBUG, file_output: bool = False) -> "LogFactory":
        """
        Initializes and returns a singleton instance of LogFactory.

        :param level: Logging level.
        :return: Singleton LogFactory instance.
        """
        cls._instance = LogFactory(level, file_output)
        return cls._instance

    @classmethod
    def singleton(cls) -> "LogFactory":
        """
        Returns the singleton instance of LogFactory.
        If it hasn't been initialized yet, it initializes it with default parameters for testing.

        :return: Singleton LogFactory instance.
        """
        return cls._instance or cls.initialize()
