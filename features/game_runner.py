"""
A feature provider for executing the main game command and any forked commands
"""

import subprocess
from typing import override

from core import FeatureProvider, RuntimeConfiguration
from core.configuration_property import ConfigurationProperty
from core.runtime_configuration import COMMAND_TRAINER

RUN_CUSTOM_GAME_EXE_PROPERTY = ConfigurationProperty(
    "RUN_CUSTOM_GAME_EXE",
    "Allows specifying the main game executable to run, relative to the game directory.",
    None,
)


class GameRunner(FeatureProvider):
    """
    A feature provider for executing the main game command and any forked
    commands using the runtime configuration.
    """

    def __init__(self, dry_run: bool = False):
        super().__init__([RUN_CUSTOM_GAME_EXE_PROPERTY])
        self.dry_run = dry_run

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        runtime_configuration.command = runtime_configuration.original_command
        self.logger.info(
            "Final game command: %s", " ".join(runtime_configuration.command)
        )
        return runtime_configuration

    @override
    def execute_in_pipeline(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        # Execute forked commands
        for command in runtime_configuration.fork_commands or []:
            if (
                command.category == COMMAND_TRAINER
                and not runtime_configuration.execute_trainers
            ):
                continue  # Skip trainer commands if trainers are disabled

            full_command = f"{command.command} {command.args or ''}"
            self.run_command(full_command, category=command.category or "Uncategorized")

        # Execute main game command
        full_command = " ".join(runtime_configuration.command or [])
        self.run_command(full_command)

    def run_command(self, command: str, category: str = "main game"):
        """
        Executes a given command using subprocess.

        Args:
            command (str): The command to execute.
        """
        if self.dry_run:
            self.logger.info(
                "[DRY RUN] Would execute %s command: %s", category, command
            )
            return
        try:
            self.logger.info("Executing %s command: %s", category, command)
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error("Command execution failed: %s", e)
