"""
Module for reading and building configuration from default or config files.
"""

from typing import override
from core import FeatureProvider
from core.config_storage import ConfigStorage


class ReadConfig(FeatureProvider):
    """
    Provides functionality to read and build the configuration from
    default, global, and game-specific sources. Ensures that the
    configurations are stored and updated as required.

    Inherits from FeatureProvider to utilize its configuration
    management capabilities.
    """

    def __init__(self, config_storage: ConfigStorage):
        super().__init__([])
        self.config_storage = config_storage
        self.global_config = {}

    @override
    def build_configuration(
        self, sourced_configuration: dict, game_id: str, app_id: str
    ) -> dict:
        sourced_configuration = super().build_configuration(
            sourced_configuration, game_id, app_id
        )
        # At this point, sourced_configuration contains all default configurations

        self.global_config = self.config_storage.get_global_config() or {}
        sourced_configuration.update(self.global_config)
        # Persist the global configuration back to storage
        # Applies any new defaults that were not present before
        self.global_config = sourced_configuration.copy()
        self.config_storage.save_global_config(self.global_config)

        self.logger.info("Global configuration loaded and applied.")

        # Check for game-specific configuration file
        game_config = self.config_storage.get_game_config(game_id or app_id)
        if game_config is None:
            # Create game-specific configuration file if it doesn't exist with empty config
            self.config_storage.save_game_config({}, game_id or app_id)
        sourced_configuration.update(game_config or {})
        self.logger.info("Game-specific configuration loaded and applied.")
        return sourced_configuration
