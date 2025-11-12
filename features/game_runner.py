"""
A feature provider for executing the main game command and any forked commands
"""

from typing import override
from core import FeatureProvider, RuntimeConfiguration
from core.runtime_configuration import COMMAND_TRAINER


class GameRunner(FeatureProvider):
    """
    A feature provider for executing the main game command and any forked
    commands using the runtime configuration.
    """

    def __init__(self):
        super().__init__([])

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        self.logger.info(
            "Original game command: %s",
            " ".join(runtime_configuration.original_command),
        )
        runtime_configuration.command = runtime_configuration.original_command
        self.logger.info(
            "Final game command: %s", " ".join(runtime_configuration.command)
        )
        return runtime_configuration

    @override
    def execute_in_pipeline(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        for command in runtime_configuration.fork_commands or []:
            if (
                command.category == COMMAND_TRAINER
                and not runtime_configuration.execute_trainers
            ):
                # Skip trainer commands if trainers are disabled
                continue

            # TODO: Execute forked command here
            self.logger.info(
                "Executing forked command (%s): %s %s",
                command.category or "Uncategorized",
                command.command,
                command.args or "",
            )

        # TODO: Execute main game command here
        self.logger.info(
            "Executing main game command: %s", runtime_configuration.command
        )
