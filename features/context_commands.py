"""Module providing context command features to be executed before startup and after exit."""

from typing import override
from core.configuration_property import ConfigurationProperty
from core.configuration_types import ConfigurationDictionary
from core.feature_provider import FeatureProvider
from core.process_runner import run_command
from core.runtime_configuration import RuntimeConfiguration

CONTEXT_COMMAND_BEFORE_STARTUP_PROPERTY = ConfigurationProperty(
    str,
    "CONTEXT_COMMAND_BEFORE_STARTUP",
    "Comand to run before starting the game",
    "Command that will be executed before starting the game.",
)

CONTEXT_COMMAND_AFTER_EXIT_PROPERTY = ConfigurationProperty(
    str,
    "CONTEXT_COMMAND_AFTER_EXIT",
    "Comand to run after exiting the game",
    "Command that will be executed after exiting the game.",
)


class ContextCommands(FeatureProvider):
    """
    Feature provider for context commands, enabling configuration of commands to be
    executed before the game starts and after the game exits.

    This class allows the user to define and manage context commands that are executed
    before the startup and after the exit of a game. It also inherits from the
    `FeatureProvider` to integrate these commands into the existing feature setup.

    Attributes:
        - CONTEXT_COMMAND_BEFORE_STARTUP_PROPERTY: Property for the command
          to execute before startup.
        - CONTEXT_COMMAND_AFTER_EXIT_PROPERTY: Property for the command to execute after exit.

    Methods:
        - before_execution: Handles the execution of commands before the game starts.
        - after_execution: Handles the execution of commands after the game ends.
    """

    def __init__(self):
        super().__init__(
            "Context Commands",
            [
                CONTEXT_COMMAND_BEFORE_STARTUP_PROPERTY,
                CONTEXT_COMMAND_AFTER_EXIT_PROPERTY,
            ],
            "Game Execution",
        )

    @override
    def before_execution(
        self,
        configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ):
        before_command = CONTEXT_COMMAND_BEFORE_STARTUP_PROPERTY.get(configuration)
        if not before_command:
            self.logger.info("No before startup command configured.")
            return

        before_process = run_command(
            before_command,
            self.logger,
            dry_run=_runtime_configuration.dry_run,
        )
        if before_process:
            with before_process:
                self.logger.info(
                    "Launched 'before startup process' with PID: %s", before_process.pid
                )
                result = before_process.wait()
                self.logger.info(
                    "'Before startup process' exited with return code: %s", result
                )

    @override
    def after_execution(
        self,
        _configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ):
        after_command = CONTEXT_COMMAND_AFTER_EXIT_PROPERTY.get(_configuration)
        if not after_command:
            self.logger.info("No after exit command configured.")
            return
        after_process = run_command(
            after_command,
            self.logger,
            dry_run=_runtime_configuration.dry_run,
        )
        if after_process:
            with after_process:
                self.logger.info(
                    "Launched 'after exit process' with PID: %s", after_process.pid
                )
                result = after_process.wait()
                self.logger.info(
                    "'After exit process' exited with return code: %s", result
                )
