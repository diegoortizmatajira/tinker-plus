"""
The RuntimeProvider module is responsible executing the game using the appropriate
runtime configuration. It manages the merging of global and game-specific settings,
as well as feature-specific customizations to build a comprehensive runtime environment.
"""

import logging
import os

from typing import List
from .runtime_configuration import RuntimeConfiguration
from .feature_provider import FeatureProvider

EMPTY = "(not provided)"


class RuntimeProvider:
    """
    The RuntimeProvider is responsible for managing the runtime configuration and operations.

    This class initializes and builds the runtime configuration by merging global
    and game-specific settings, as well as feature-specific customizations. It also
    manages the execution of the runtime environment using the built configuration.

    Attributes:
        configuration (dict): The merged runtime configuration containing global,
            game-specific, and feature-specific settings.
        runtime_configuration (Optional[RuntimeConfiguration]): The active runtime
            configuration used for executing the environment. Defaults to None.
        features (List[FeatureProvider]): A list of feature providers that contribute
            to building the runtime configuration.
    """

    def __init__(self, features: List[FeatureProvider]):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.configuration: dict = {}
        self.features = features
        self.runtime_configuration = RuntimeConfiguration()
        self.read_steam_context()

    def read_steam_context(self):
        """
        Reads the Steam context for the runtime configuration.

        This method retrieves the Steam-specific environment variables such as
        `STEAM_APP_ID`, `STEAM_GAME_ID`, `STEAM_COMPAT_INSTALL_PATH`, and
        `STEAM_COMPAT_DATA_PATH`, and updates the runtime configuration with their
        values. If the environment variables are not present, it retains the default
        values in the runtime configuration.

        The method also logs the retrieved values or indicates if they are not provided.

        Updates:
            - steam_app_id: Steam application ID.
            - steam_game_id: Steam game ID.
            - steam_compat_install_path: Path to the Steam compatibility installation directory.
            - steam_compat_data_path: Path to the Steam compatibility data directory.
            - prefix_path: Path to the default prefix directory derived from
              `steam_compat_data_path`.
        """
        self.runtime_configuration.steam_app_id = (
            os.getenv("STEAM_APP_ID") or self.runtime_configuration.steam_app_id
        )
        self.logger.info(
            "Steam App ID: %s", self.runtime_configuration.steam_app_id or EMPTY
        )
        self.runtime_configuration.steam_game_id = (
            os.getenv("STEAM_GAME_ID") or self.runtime_configuration.steam_game_id
        )
        self.logger.info(
            "Steam Game ID: %s", self.runtime_configuration.steam_game_id or EMPTY
        )
        self.runtime_configuration.steam_compat_install_path = (
            os.getenv("STEAM_COMPAT_INSTALL_PATH")
            or self.runtime_configuration.steam_compat_install_path
        )
        self.logger.info(
            "Steam Compat Install Path: %s",
            self.runtime_configuration.steam_compat_install_path or EMPTY,
        )
        self.runtime_configuration.steam_compat_data_path = (
            os.getenv("STEAM_COMPAT_DATA_PATH")
            or self.runtime_configuration.steam_compat_data_path
        )
        self.logger.info(
            "Steam Compat Data Path: %s",
            self.runtime_configuration.steam_compat_data_path or EMPTY,
        )
        self.runtime_configuration.prefix_path = (
            f"{self.runtime_configuration.steam_compat_data_path}/pfx"
        )

    def build_configuration(self):
        """
        Builds the runtime configuration by merging global and game-specific configurations,
        and applies feature-specific customizations.

        The method performs the following steps:
        - Reads global and game-specific configurations.
        - Merges the configurations.
        - Builds the feature configurations by calling `build_configuration` on each feature.
        - Applies the configuration to the runtime environment using `apply_configuration`.

        Raises:
            RuntimeError: If any critical configuration step fails.
        """
        # TODO: Read global configuration from file or environment
        global_configuration = {}
        # TODO: Read game-specific configuration from file or environment
        game_configuration = {}
        # Merge configurations
        self.configuration.update(global_configuration)
        self.configuration.update(game_configuration)
        # Fills any missing configuration with defaults from features
        for feature in self.features:
            self.configuration = feature.build_configuration(
                self.configuration,
                self.runtime_configuration.steam_game_id or "unknown",
                self.runtime_configuration.steam_app_id or "unknown",
            )
        # Apply configurations to runtime
        for feature in self.features:
            feature.try_apply_configuration(
                self.configuration, self.runtime_configuration
            )

    def run(self, run_with_trainers: bool = True):
        """
        Runs the runtime environment using the built configuration.

        This method ensures that the runtime configuration is initialized
        and then proceeds with the execution. If the runtime configuration is
        not built, an exception is raised.
        Args:
            update_configuration (Callable): A function that takes the current
                runtime configuration and returns an updated configuration.
                Defaults to an identity function.

        Raises:
            RuntimeError: If the runtime configuration has not been built.
        """
        if self.runtime_configuration is None:
            raise RuntimeError("Runtime configuration has not been built.")

        self.runtime_configuration.execute_trainers = run_with_trainers

        for features in self.features:
            features.execute_in_pipeline(self.configuration, self.runtime_configuration)
