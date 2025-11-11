"""
The RuntimeProvider module is responsible executing the game using the appropriate
runtime configuration. It manages the merging of global and game-specific settings,
as well as feature-specific customizations to build a comprehensive runtime environment.
"""

from typing import Callable, List, Optional
from .runtime_configuration import RuntimeConfiguration
from .feature_provider import FeatureProvider


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
        self.configuration: dict = {}
        self.runtime_configuration: Optional[RuntimeConfiguration] = None
        self.features = features

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
            self.configuration = feature.build_configuration(self.configuration)
        # Apply configurations to runtime
        self.runtime_configuration = RuntimeConfiguration()
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
