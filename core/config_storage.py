import json
import logging
import os
from typing import Optional

from core.defaults import (
    CONFIG_LOCATION,
    GAME_CONFIG_DIR,
    GAME_CONFIG_FILE_TEMPLATE,
    GLOBAL_CONFIG_FILE,
)


class ConfigStorage:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_global_config(self) -> Optional[dict]:
        if not os.path.exists(GLOBAL_CONFIG_FILE):
            return None
        self.logger.info("Loading global configuration from: %s", GLOBAL_CONFIG_FILE)
        with open(GLOBAL_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_game_config(self, game_id: str) -> Optional[dict]:
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
        if not os.path.exists(GLOBAL_CONFIG_FILE):
            self.logger.warning(
                "Creating global configuration file at: %s", GLOBAL_CONFIG_FILE
            )
        else:
            self.logger.info("Updating global configuration at: %s", GLOBAL_CONFIG_FILE)
        os.makedirs(CONFIG_LOCATION, exist_ok=True)
        # Convert sourced_configuration to json and save to GLOBAL_CONFIG_FILE
        global_json_content = json.dumps(config, indent=4)
        with open(GLOBAL_CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(global_json_content)

    def save_game_config(self, config: dict, game_id: str):
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
