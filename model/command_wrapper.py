"""
This module defines the CommandWrapper class, which represents a pipeline
wrapper with environment variables and a command to execute. The CommandWrapper
class provides functionality to wrap a given pipeline assembled command using a
specified wrapper function or by concatenating a command string.
"""

from collections.abc import Sequence
import logging
from dataclasses import dataclass
from typing import Callable

from model.command import CommandCategory


@dataclass
class CommandWrapper[T]:
    """
    Represents a pipeline wrapper with environment variables and a command to execute.
    """

    command: str | None = None
    wrapper: Callable[[str, T], str] | None = None
    applies_for: Sequence[CommandCategory] | None = None

    def wrap(
        self,
        pipeline_assembled_command: str,
        parameter: T,
        *,
        command_category: CommandCategory | None = None,
        logger: logging.Logger,
    ) -> str:
        """
        Wraps the provided pipeline assembled command using the defined wrapper.

        If a wrapper is defined, it applies the wrapper function to the pipeline
        assembled command. Otherwise, it concatenates the command and the pipeline
        assembled command.

        Args:
            pipeline_assembled_command (str): The assembled command to be wrapped.

        Returns:
            str: The wrapped command.
        """
        # If no specific command category is provided, default to applying for GAME category only.
        applies_for_with_default = self.applies_for or [CommandCategory.GAME]
        if not (command_category and command_category in applies_for_with_default):
            # If the wrapper does not apply for the given command category,
            # return the original command.
            return pipeline_assembled_command

        if self.wrapper:
            wrapped_command = self.wrapper(pipeline_assembled_command, parameter)
        else:
            wrapped_command = f"{self.command} {pipeline_assembled_command}"
        logger.debug("Wrapped command build step: %s", wrapped_command)
        return wrapped_command
