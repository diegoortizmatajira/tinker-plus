"""
A feature provider for executing the main game command and any forked commands
"""

from typing import override

from core import FeatureProvider, RuntimeConfiguration
from core.configuration_property import ConfigurationProperty
from core.process_runner import run_game_and_forks_with_compatibility_tool


GAME_CUSTOM_EXE_PROPERTY = ConfigurationProperty(
    str,
    "GAME_CUSTOM_EXE",
    "Custom Game Executable",
    "Allows specifying the main game executable to run.",
    None,
)
GAME_CUSTOM_ARGS_PROPERTY = ConfigurationProperty(
    str,
    "GAME_CUSTOM_ARGS",
    "Custom Game Arguments",
    "Allows specifying additional arguments for the game executable.",
    None,
)
GAME_RUN_FORKS_ONLY_PROPERTY = ConfigurationProperty(
    bool,
    "GAME_RUN_FORKS_ONLY",
    "Run Forked Commands Only",
    "If set to 'True', only the forked commands will be executed, skipping the main game command.",
    default=False,
)


class GameRunner(FeatureProvider):
    """
    A feature provider for executing the main game command and any forked
    commands using the runtime configuration.
    """

    def __init__(self):
        super().__init__(
            "Game Runner",
            [
                GAME_CUSTOM_EXE_PROPERTY,
                GAME_CUSTOM_ARGS_PROPERTY,
                GAME_RUN_FORKS_ONLY_PROPERTY,
            ],
            "General",
        )

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        runtime_configuration.execute_forks_only = GAME_RUN_FORKS_ONLY_PROPERTY.get(
            configuration, False
        )
        if runtime_configuration.execute_forks_only:
            self.logger.info(
                "Configured to run only forked commands, skipping main game."
            )
        custom_exe = GAME_CUSTOM_EXE_PROPERTY.get(configuration)
        if custom_exe:
            runtime_configuration.steam_game_exe = custom_exe
            self.logger.info("Using custom game executable: %s", custom_exe)

        custom_args = GAME_CUSTOM_ARGS_PROPERTY.get(configuration)
        if custom_args:
            runtime_configuration.steam_game_args = custom_args
            self.logger.info("Using custom game arguments: %s", custom_args)
        return runtime_configuration

    @override
    def execute_in_pipeline(
        self, _configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        for k, v in (runtime_configuration.environment_variables or {}).items():
            self.logger.info("Using environment:  %s=%s", k, v)
        run_game_and_forks_with_compatibility_tool(runtime_configuration, self.logger)
