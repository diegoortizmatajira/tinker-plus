"""
A feature provider for executing the main game command and any forked commands
"""

from typing import override

from core import FeatureProvider, RuntimeConfiguration
from core.configuration_property import ConfigurationProperty
from core.process_runner import run_game_and_forks_with_compatibility_tool


GAME_CUSTOM_EXE_PROPERTY = ConfigurationProperty(
    "GAME_CUSTOM_EXE",
    "Allows specifying the main game executable to run.",
    None,
)
GAME_CUSTOM_ARGS_PROPERTY = ConfigurationProperty(
    "GAME_CUSTOM_ARGS",
    "Allows specifying additional arguments for the game executable.",
    None,
)


class GameRunner(FeatureProvider):
    """
    A feature provider for executing the main game command and any forked
    commands using the runtime configuration.
    """

    def __init__(self):
        super().__init__(
            [
                GAME_CUSTOM_EXE_PROPERTY,
                GAME_CUSTOM_ARGS_PROPERTY,
            ]
        )

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        runtime_configuration.steam_game_exe = (
            configuration.get(GAME_CUSTOM_EXE_PROPERTY.name)
            or runtime_configuration.steam_game_exe
        )
        return runtime_configuration

    @override
    def execute_in_pipeline(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        for k, v in (runtime_configuration.environment_variables or {}).items():
            self.logger.info("Using:  %s=%s", k, v)
        run_game_and_forks_with_compatibility_tool(runtime_configuration, self.logger)
