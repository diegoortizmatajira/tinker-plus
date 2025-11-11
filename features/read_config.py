import os
from typing import override
from core import (
    FeatureProvider,
)
from core.defaults import CONFIG_LOCATION, GAME_CONFIG_FILE_TEMPLATE, GLOBAL_CONFIG_FILE


class ReadConfig(FeatureProvider):
    def __init__(self):
        super().__init__([])

    @override
    def build_configuration(
        self, sourced_configuration: dict, game_id: str, app_id: str
    ) -> dict:
        # If configuration folder does not exist, create it
        os.makedirs(os.path.dirname(CONFIG_LOCATION), exist_ok=True)

        self.logger.info("Reading global configuration from: %s", GLOBAL_CONFIG_FILE)
        game_configuration_file = str.format(
            GAME_CONFIG_FILE_TEMPLATE, game_id or app_id
        )
        self.logger.info("Reading game configuration from: %s", game_configuration_file)
        return {
            "USE_PROTON": "PROTON_7_0",
            "WEMOD_ENABLED": "1",
            "WEMOD_PATH": "/path/to/wemod/executable",
        }
