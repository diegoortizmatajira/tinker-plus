"""
A feature provider for executing the main game command and any forked commands
"""

from typing import override

from core import (
    FeatureProvider,
    ConfigurationProperty,
    ProcessRunner,
)
from core.defaults import CWD_DIR_NAME
from model import (
    Command,
    CommandCategory,
    RuntimeConfiguration,
    ConfigurationDictionary,
)

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
GAME_CUSTOM_CWD_PROPERTY = ConfigurationProperty(
    str,
    "GAME_CUSTOM_CWD",
    "Custom Game Working Directory",
    "Allows specifying a custom working directory for the game executable.",
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
                GAME_CUSTOM_CWD_PROPERTY,
                GAME_RUN_FORKS_ONLY_PROPERTY,
            ],
            "Game Execution",
        )

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        runtime_configuration.execute_forks_only = GAME_RUN_FORKS_ONLY_PROPERTY.get(
            configuration, False
        )
        if runtime_configuration.execute_forks_only:
            self.logger.info(
                "Configured to run only forked commands, skipping main game."
            )
        if not runtime_configuration.game_executable_command:
            runtime_configuration.game_executable_command = Command(
                "echo", category=CommandCategory.GAME
            )

        custom_exe = GAME_CUSTOM_EXE_PROPERTY.get(configuration)
        if custom_exe:
            runtime_configuration.game_executable_command.command = custom_exe
            self.logger.info("Using custom game executable: %s", custom_exe)

        custom_args = GAME_CUSTOM_ARGS_PROPERTY.get(configuration)
        if custom_args:
            runtime_configuration.game_executable_command.args = custom_args
            self.logger.info("Using custom game arguments: %s", custom_args)
        custom_cwd = GAME_CUSTOM_CWD_PROPERTY.get(configuration)
        runtime_configuration.game_executable_command.cwd = (
            custom_cwd
            or runtime_configuration.steam_environment_data.steam_compat_install_path
            or f"{runtime_configuration.prefix_path}/{CWD_DIR_NAME}"
        )
        self.logger.info(
            "Using game working directory: %s",
            runtime_configuration.game_executable_command.cwd,
        )
        return runtime_configuration

    @override
    def execute_in_pipeline(
        self,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        if runtime_configuration.execute_forks_only:
            self.logger.info(
                "Skipping main game execution as configured to run only forked commands."
            )
            return

        if not runtime_configuration.game_executable_command:
            self.logger.error("No game executable specified to run.")
            raise RuntimeError("No game executable specified to run.")

        game_process = ProcessRunner.run_with_pipeline(
            runtime_configuration.game_executable_command,
            runtime_configuration,
            self.logger,
        )
        if game_process:
            with game_process:
                self.logger.info("Launched game with PID: %s", game_process.pid)
                result = game_process.wait()
                self.logger.info("Game process exited with return code: %s", result)
