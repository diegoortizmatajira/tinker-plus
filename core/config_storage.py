"""Module for managing configuration storage, including global and game-specific"""

import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import cast, final

from model import GameInfo, ConfigurationDictionary
from defaults import (
    CONFIG_LOCATION,
    GAME_CONFIG_DIR,
    GAME_CONFIG_FILE_TEMPLATE,
    GAME_INFO_KEY,
    GLOBAL_CONFIG_FILE,
)
from .feature_provider import FeatureProvider
from .log_storage import LogFactory


@final
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

    def get_game_configuration_files(self) -> list[Path]:
        """
        Retrieves all game configuration files based on the GAME_CONFIG_FILE_TEMPLATE.

        Returns:
            list[Path]: A list of Paths to the game configuration files.
        """
        config_files: list[Path] = []
        config_dir = Path(GAME_CONFIG_DIR)
        for file in config_dir.glob("*.json"):
            if file.is_file():
                config_files.append(file)
        return config_files

    def get_global_config(self) -> ConfigurationDictionary | None:
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
            return cast(ConfigurationDictionary, json.load(f))

    def get_game_config(self, game_id: str) -> ConfigurationDictionary | None:
        """
        Retrieve the game-specific configuration for a given game ID.

        This method loads the configuration file for the specified game ID and
        returns its content as a dictionary. If the file does not exist, it returns None.

        Args:
            game_id (str): The unique identifier of the game whose configuration is to be retrieved.

        Returns:
            dict | None: The contents of the game-specific configuration file if it exists,
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
            return cast(ConfigurationDictionary, json.load(f))

    def save_global_config(self, config: ConfigurationDictionary):
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
            _ = f.write(global_json_content)

    def save_game_config(
        self,
        config: ConfigurationDictionary,
        game_id: str | None,
        global_config: ConfigurationDictionary | None,
    ):
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
        game_configuration_file = str.format(
            GAME_CONFIG_FILE_TEMPLATE, game_id or "unknown"
        )
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
        # Calculate the diff if global_config is provided
        if global_config is not None:
            config = self.__diff_configs(global_config, config)
        # Convert sourced_configuration to json and save to game_configuration_file
        game_json_content = json.dumps(config, indent=4, sort_keys=True)
        with open(game_configuration_file, "w", encoding="utf-8") as f:
            _ = f.write(game_json_content)

    def __diff_configs(
        self,
        global_config: ConfigurationDictionary,
        game_config: ConfigurationDictionary,
    ) -> ConfigurationDictionary:
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
        diff: ConfigurationDictionary = {}
        for key, value in game_config.items():
            if key not in global_config or global_config[key] != value:
                diff[key] = value
        return diff

    def build_global_configuration(
        self,
        sourced_configuration: ConfigurationDictionary,
        clone_configuration: bool = False,
    ) -> ConfigurationDictionary:
        """
        Build the global configuration.

        This method constructs the global configuration by merging the provided
        sourced configuration with the existing global configuration from storage.
        The option to clone the sourced configuration ensures that the original
        source remains unaltered during the update process. Once merged, the global
        configuration is persisted back to storage, applying any new defaults added.

        Args:
            - sourced_configuration (dict): The configuration data to merge with the global
              configuration.
            - clone_configuration (bool): Whether to clone the sourced configuration before
              updating.

        Returns:
            dict: The finalized global configuration after merging and persisting the changes.
        """
        global_config = self.get_global_config() or {}
        target_configuration = sourced_configuration
        if clone_configuration:
            target_configuration = sourced_configuration.copy()
        target_configuration.update(global_config)
        # Persist the global configuration back to storage
        # Applies any new defaults that were not present before
        self.save_global_config(target_configuration)
        return target_configuration

    def build_game_configuration(
        self,
        game_info: GameInfo,
        sourced_configuration: ConfigurationDictionary,
        global_configuration_snapshot: ConfigurationDictionary,
        clone_configuration: bool = False,
    ) -> ConfigurationDictionary:
        """
        Build the game-specific configuration.

        This method constructs the game-specific configuration by merging the provided
        sourced configuration with any existing configuration for the given game. If no
        configuration exists for the game, a new one is created and saved.

        The option to clone the sourced configuration ensures that the original source
        remains unaltered during the update process. The game information is included
        in the configuration under a designated key for reference.

        Args:
            game_info (GameInfo): The game information object containing the unique game ID.
            sourced_configuration (dict): The source configuration data to be merged with
                                           the game's specific configuration.
            global_configuration_snapshot (dict): A snapshot of the global configuration,
                                                  used to calculate configuration differences.
            clone_configuration (bool): Whether to clone the sourced configuration before merging.

        Returns:
            dict: The finalized game-specific configuration after merging and saving the changes.
        """
        # Check for game-specific configuration file
        game_config = self.get_game_config(game_info.game_id)
        target_configuration = sourced_configuration
        if clone_configuration:
            target_configuration = sourced_configuration.copy()

        target_configuration.update(game_config or {})
        # Includes game-info in the configuration for reference
        target_configuration[GAME_INFO_KEY] = game_info.__dict__
        if game_config is None:
            # Create game-specific configuration file if it doesn't exist with empty config
            self.save_game_config(
                target_configuration,
                game_info.game_id,
                global_configuration_snapshot,
            )
        return target_configuration

    def validate_config(
        self, game: GameInfo, features: Sequence[FeatureProvider]
    ) -> list[str]:
        """
        Validate the configuration for the provided game and features.

        This method ensures that the game-specific configuration contains all expected keys
        based on the provided features and warns about any unexpected keys.

        Args:
            game (GameInfo): The game information object for which the configuration is validated.
            features (list[FeatureProvider]): A list of feature providers whose properties
                                              determine the expected configuration keys.

        Returns:
            list[str]: A list of error messages indicating unexpected configuration keys.
        """
        expected_config_keys = [GAME_INFO_KEY]
        for feature in features:
            expected_config_keys.extend(
                [property.name for property in feature.properties]
            )
        errors: list[str] = []

        global_config = self.build_global_configuration({})
        game_specific_config = self.build_game_configuration(
            game,
            global_config,
            global_config,
            True,
        )
        for k, _ in game_specific_config.items():
            if k not in expected_config_keys:
                self.logger.warning(
                    "Unexpected config key '%s' in game '%s' (%s).",
                    k,
                    game.name,
                    game.game_id,
                )
                errors.append(f"Unexpected config key: {k}")

        # Save an updated config file
        self.save_game_config(game_specific_config, game.game_id, global_config)
        return errors
