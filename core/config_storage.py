"""Module for managing configuration storage, including global and game-specific"""

import json
import os
from typing import Optional

from core.defaults import (
    CONFIG_LOCATION,
    GAME_CONFIG_DIR,
    GAME_CONFIG_FILE_TEMPLATE,
    GLOBAL_CONFIG_FILE,
)

from .log_storage import LogFactory


class ConfigStorage:
    """
    A class for handling storage and management of configuration files, including
    global and game-specific configurations. Provides methods for loading,
    saving, and updating configuration data.

    Attributes:
        logger: A logger instance for logging operations within the class.
    """

    def __init__(self):
        self.logger = LogFactory.singleton().get_logger(self.__class__.__name__)

    def get_global_config(self) -> Optional[dict]:
        """
        Retrieve the global configuration.

        This method loads the global configuration file and returns its content
        as a dictionary. If the file does not exist, it returns None.

        Returns:
            dict: The contents of the global configuration file if it exists,
            otherwise None.
        """
        if not os.path.exists(GLOBAL_CONFIG_FILE):
            return None
        self.logger.info("Loading global configuration from: %s", GLOBAL_CONFIG_FILE)
        with open(GLOBAL_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_game_config(self, game_id: str) -> Optional[dict]:
        """
        Retrieve the game-specific configuration for a given game ID.

        This method loads the configuration file for the specified game ID and
        returns its content as a dictionary. If the file does not exist, it returns None.

        Args:
            game_id (str): The unique identifier of the game whose configuration is to be retrieved.

        Returns:
            Optional[dict]: The contents of the game-specific configuration file if it exists,
            otherwise None.
        """
        game_configuration_file = str.format(GAME_CONFIG_FILE_TEMPLATE, game_id)
        if not os.path.exists(game_configuration_file):
            return None
        self.logger.info(
            "Loading game-specific configuration from: %s",
            game_configuration_file,
        )
        with open(game_configuration_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_global_config(self, config: dict):
        """
        Save the global configuration.

        This method saves the provided global configuration dictionary to the global
        configuration file. If the file does not exist, it creates a new one.
        If the file exists, it updates its contents.

        Args:
            config (dict): The global configuration data to be saved, represented as a dictionary.
        """
        if not os.path.exists(GLOBAL_CONFIG_FILE):
            self.logger.warning(
                "Creating global configuration file at: %s", GLOBAL_CONFIG_FILE
            )
        else:
            self.logger.info("Updating global configuration at: %s", GLOBAL_CONFIG_FILE)
        os.makedirs(CONFIG_LOCATION, exist_ok=True)
        # Convert sourced_configuration to json and save to GLOBAL_CONFIG_FILE
        global_json_content = json.dumps(config, indent=4, sort_keys=True)
        with open(GLOBAL_CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(global_json_content)

    def save_game_config(self, config: dict, game_id: str):
        """
        Save the game-specific configuration for a given game ID.
        This method saves the provided game-specific configuration dictionary to the
        configuration file corresponding to the specified game ID. If the file does
        not exist, it creates a new one. If the file exists, it updates its contents.

        Args:
            config (dict): The game-specific configuration data to be saved,
            represented as a dictionary.
            game_id (str): The unique identifier of the game whose configuration is to be saved.
        """
        game_configuration_file = str.format(GAME_CONFIG_FILE_TEMPLATE, game_id)
        if not os.path.exists(game_configuration_file):
            self.logger.warning(
                "Creating game-specific configuration file at: %s",
                game_configuration_file,
            )
        else:
            self.logger.info(
                "Updating game-specific configuration at: %s", game_configuration_file
            )
        os.makedirs(GAME_CONFIG_DIR, exist_ok=True)
        # Convert sourced_configuration to json and save to game_configuration_file
        game_json_content = json.dumps(config, indent=4)
        with open(game_configuration_file, "w", encoding="utf-8") as f:
            f.write(game_json_content)

    def _diff_configs(self, global_config: dict, game_config: dict) -> dict:
        """
        Compute the difference between global and game-specific configurations.

        This method identifies the differences between the provided global and
        game-specific configuration dictionaries. It returns a new dictionary
        containing only the key-value pairs that differ in the game-specific
        configuration compared to the global configuration.

        Args:
            global_config (dict): The global configuration
            game_config (dict): The game-specific configuration
        Returns:
            dict: A dictionary containing only the differing key-value pairs from
            the game-specific configuration.
        """
        diff = {}
        for key, value in game_config.items():
            if key not in global_config or global_config[key] != value:
                diff[key] = value
        return diff
