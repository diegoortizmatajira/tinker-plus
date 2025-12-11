"""
Module for reading and building configuration from default or config files.
"""

from typing import final, override
from core import FeatureProvider
from core.config_storage import ConfigStorage
from core.configuration_types import ConfigurationDictionary
from core.runtime_configuration import RuntimeConfiguration


@final
class ReadConfig(FeatureProvider):
    """
    Provides functionality to read and build the configuration from
    default, global, and game-specific sources. Ensures that the
    configurations are stored and updated as required.

    Inherits from FeatureProvider to utilize its configuration
    management capabilities.
    """

    def __init__(self, config_storage: ConfigStorage):
        super().__init__("Configuration", [], "Data Management")
        self.config_storage = config_storage

    @override
    def build_configuration(
        self,
        sourced_configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> ConfigurationDictionary:
        sourced_configuration = super().build_configuration(
            sourced_configuration, runtime_configuration
        )
        # At this point, sourced_configuration contains all default configurations
        sourced_configuration = self.config_storage.build_global_configuration(
            sourced_configuration
        )
        # Update the runtime configuration with a copy of the loaded global configuration
        runtime_configuration.loaded_global_configuration = sourced_configuration.copy()
        self.logger.info("Global configuration loaded and applied.")

        sourced_configuration = self.config_storage.build_game_configuration(
            runtime_configuration.game_info,
            sourced_configuration,
            runtime_configuration.loaded_global_configuration,
        )
        self.logger.info("Game-specific configuration loaded and applied.")
        return sourced_configuration
