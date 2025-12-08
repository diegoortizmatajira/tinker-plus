"""Module to set up logging for the application."""

import logging
import os
from pathlib import Path
import sys
from typing import Optional

from core.defaults import APP_LAST_RUN_LOG_FILE, GAME_LOGS_DIR_TEMPLATE


class LogFactory:
    """
    Factory class to set up logging for the application.
    """

    _instance: Optional["LogFactory"] = None

    def __init__(
        self,
        game_id: str,
        *,
        console_level: Optional[int] = logging.DEBUG,
        file_level: Optional[int] = None,
    ):
        logging.basicConfig(level=logging.DEBUG, handlers=[])
        self.game_id = game_id
        self.logs_folder: Optional[str] = None
        self.console_handler: Optional[logging.StreamHandler] = None
        if console_level:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setFormatter(
                logging.Formatter("%(levelname)s - [%(name)s] - %(message)s")
            )
            self.console_handler.setLevel(console_level)

        self.file_handler: Optional[logging.FileHandler] = None
        if file_level:
            self.logs_folder = LogFactory.prepare_logs_folder(game_id)
            log_filename = self.get_log_filename(APP_LAST_RUN_LOG_FILE)
            self.file_handler = logging.FileHandler(log_filename)
            self.file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
                )
            )
            self.file_handler.setLevel(file_level)

    def get_log_filename(self, file_name: str) -> str:
        """
        Generates the full path for a log file if the logs folder is configured.

        :param file_name: Name of the log file.
        :return: Full path of the log file, or None if logs folder is not set.
        """
        if self.logs_folder:
            return os.path.join(self.logs_folder, file_name)
        raise ValueError(f"Cannot determine log file path for {file_name}.")

    def get_log_folder(self) -> str:
        """
        Generates the full path for a log file if the logs folder is configured.

        :param file_name: Name of the log file.
        :return: Full path of the log file, or None if logs folder is not set.
        """
        if self.logs_folder:
            return self.logs_folder
        raise ValueError("Cannot determine log folder path.")

    def get_logger(self, name: str) -> logging.Logger:
        """
        Returns a logger configured with file and console handlers.

        :param name: Name of the logger.
        :param level: Logging level.
        :return: Configured logger instance.
        """
        logger = logging.getLogger(name)
        if self.console_handler:
            logger.addHandler(self.console_handler)
        if self.file_handler:
            logger.addHandler(self.file_handler)
        return logger

    @classmethod
    def initialize(
        cls,
        game_id: str,
        console_level: Optional[int] = logging.DEBUG,
        file_level: Optional[int] = None,
    ) -> "LogFactory":
        """
        Initializes and returns a singleton instance of LogFactory.

        :param level: Logging level.
        :return: Singleton LogFactory instance.
        """
        cls._instance = LogFactory(
            game_id,
            console_level=console_level,
            file_level=file_level,
        )
        return cls._instance

    @classmethod
    def singleton(cls) -> "LogFactory":
        """
        Returns the singleton instance of LogFactory.
        If it hasn't been initialized yet, it initializes it with default parameters for testing.

        :return: Singleton LogFactory instance.
        """
        return cls._instance or cls.initialize("test")

    @staticmethod
    def prepare_logs_folder(game_id: str) -> str:
        """
        Prepares the logging directory for a game, ensuring the appropriate
        structure and file management for new and existing logs.

        :param game_id: Unique identifier for the game.
        """
        log_folder = Path(GAME_LOGS_DIR_TEMPLATE.format(game_id))
        log_folder.mkdir(parents=True, exist_ok=True)

        for log_file in log_folder.glob("*.log"):
            old_log_file = log_file.with_suffix(".old")
            log_file.replace(old_log_file)
        return str(log_folder)
