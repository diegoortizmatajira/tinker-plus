"""
Feature provider that reads Steam context from environment variables
"""

import os
from typing import override
from core import FeatureProvider, RuntimeConfiguration


class SteamContextReader(FeatureProvider):
    def __init__(self):
        super().__init__([])

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        runtime_configuration.steam_app_id = os.getenv("STEAM_APP_ID", "")
        runtime_configuration.steam_game_id = os.getenv("STEAM_GAME_ID", "")
        runtime_configuration.steam_compat_install_path = os.getenv(
            "STEAM_COMPAT_INSTALL_PATH", ""
        )
        runtime_configuration.steam_compat_data_path = os.getenv(
            "STEAM_COMPAT_DATA_PATH", ""
        )
        self.logger.info("Steam App ID: %s", runtime_configuration.steam_app_id)
        self.logger.info("Steam Game ID: %s", runtime_configuration.steam_game_id)
        self.logger.info(
            "Steam Compat Install Path: %s",
            runtime_configuration.steam_compat_install_path,
        )
        self.logger.info(
            "Steam Compat Data Path: %s",
            runtime_configuration.steam_compat_data_path,
        )
        self.logger.info("Steam context read successfully.")
        return runtime_configuration
