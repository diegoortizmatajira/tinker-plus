"""
A feature provider for executing the main game command and any forked commands
"""

from subprocess import Popen
from time import sleep
from typing import Any, override

from core import (
    FeatureProvider,
    ProcessRunner,
)
from defaults import CWD_DIR_NAME
from model import (
    Command,
    CommandCategory,
    RuntimeConfiguration,
    ConfigurationProperty,
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

    game_process: Popen[Any] | None = None

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
            runtime_configuration.game_executable_command = Command.from_string(
                "echo", category=CommandCategory.GAME
            )

        custom_exe = GAME_CUSTOM_EXE_PROPERTY.get(configuration)
        if custom_exe:
            runtime_configuration.game_executable_command.replace_command(custom_exe)
            self.logger.info("Using custom game executable: %s", custom_exe)

        custom_args = GAME_CUSTOM_ARGS_PROPERTY.get(configuration)
        if custom_args:
            runtime_configuration.game_executable_command.replace_args(custom_args)
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

        self.game_process = ProcessRunner.run_with_pipeline(
            runtime_configuration.game_executable_command,
            runtime_configuration,
            self.logger,
        )
        if self.game_process:
            self.logger.info("Launched game with PID: %s", self.game_process.pid)
        else:
            self.logger.error("Failed to launch the game process.")
            raise RuntimeError("Failed to launch the game process.")

    @override
    def wait_for_completion(
        self,
        _configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ):
        if self.game_process:
            # Wait for the game process to exit if it's still running
            with self.game_process:
                result = self.game_process.wait()
                self.logger.info("Game process exited with return code: %s", result)
