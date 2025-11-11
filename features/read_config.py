"""
Module for reading and building configuration from default or config files.
"""

import os
import json
from typing import override
from core import (
    FeatureProvider,
)
from core.defaults import (
    CONFIG_LOCATION,
    GAME_CONFIG_DIR,
    GAME_CONFIG_FILE_TEMPLATE,
    GLOBAL_CONFIG_FILE,
)


class ReadConfig(FeatureProvider):
    """
    Provides functionality to read and build the configuration from
    default, global, and game-specific sources. Ensures that the
    configurations are stored and updated as required.

    Inherits from FeatureProvider to utilize its configuration
    management capabilities.
    """

    def __init__(self):
        super().__init__([])

    @override
    def build_configuration(
        self, sourced_configuration: dict, game_id: str, app_id: str
    ) -> dict:
        sourced_configuration = super().build_configuration(
            sourced_configuration, game_id, app_id
        )
        # At this point, sourced_configuration contains all default configurations
        # Check if global configuration file exists
        if not os.path.exists(GLOBAL_CONFIG_FILE):
            self.logger.warning(
                "Creating global configuration file at: %s", GLOBAL_CONFIG_FILE
            )
            os.makedirs(CONFIG_LOCATION, exist_ok=True)
            # Convert sourced_configuration to json and save to GLOBAL_CONFIG_FILE
            global_json_content = json.dumps(sourced_configuration, indent=4)
            with open(GLOBAL_CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(global_json_content)
        else:
            self.logger.info(
                "Reading global configuration from: %s", GLOBAL_CONFIG_FILE
            )
            # Load global configuration and update sourced_configuration
            with open(GLOBAL_CONFIG_FILE, "r", encoding="utf-8") as f:
                global_config = json.load(f)
                sourced_configuration.update(global_config)

        game_configuration_file = str.format(
            GAME_CONFIG_FILE_TEMPLATE, game_id or app_id
        )
        # Check for game-specific configuration file
        if not os.path.exists(game_configuration_file):
            self.logger.warning(
                "Creating game-specific configuration file at: %s",
                game_configuration_file,
            )
            os.makedirs(GAME_CONFIG_DIR, exist_ok=True)
            # Convert sourced_configuration to json and save to game_configuration_file
            game_json_content = json.dumps({}, indent=4)
            with open(game_configuration_file, "w", encoding="utf-8") as f:
                f.write(game_json_content)
        else:
            self.logger.info(
                "Reading game-specific configuration from: %s",
                game_configuration_file,
            )
            with open(game_configuration_file, "r", encoding="utf-8") as f:
                game_config = json.load(f)
                sourced_configuration.update(game_config)
        return sourced_configuration
