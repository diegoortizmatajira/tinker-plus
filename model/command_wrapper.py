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

from model.command import Command, CommandCategory


@dataclass
class CommandWrapper[T]:
    """
    Represents a pipeline wrapper with environment variables and a command to execute.
    """

    wrapper: Callable[[Command, T], Command]
    applies_for: Sequence[CommandCategory] | None = None
    use_in_script: bool = False

    @classmethod
    def from_command_str(
        cls,
        command: str,
        *,
        applies_for: Sequence[CommandCategory] | None = None,
        use_in_script: bool = False,
    ) -> "CommandWrapper":
        """
        Creates a CommandWrapper instance from a Command object.

        Args:
            command (Command): The command to be wrapped.
            applies_for (Sequence[CommandCategory] | None): Optional sequence
            of command categories for which the wrapper applies.
        Returns:
            CommandWrapper: A new instance of CommandWrapper with the specified
            command and applies_for categories.
        """
        return cls.from_command(
            Command.from_string(command),
            applies_for=applies_for,
            use_in_script=use_in_script,
        )

    @classmethod
    def from_command(
        cls,
        command: Command,
        *,
        applies_for: Sequence[CommandCategory] | None = None,
        use_in_script: bool = False,
    ) -> "CommandWrapper":
        """
        Creates a CommandWrapper instance from a Command object.

        Args:
            command (Command): The command to be wrapped.
            applies_for (Sequence[CommandCategory] | None): Optional sequence
            of command categories for which the wrapper applies.
        Returns:
            CommandWrapper: A new instance of CommandWrapper with the specified
            command and applies_for categories.
        """
        return cls(
            wrapper=lambda pipeline_command, _: Command(
                internal_representation=[command, pipeline_command]
            ),
            applies_for=applies_for,
            use_in_script=use_in_script,
        )

    def wrap(
        self,
        pipeline_assembled_command: Command,
        parameter: T,
        *,
        command_category: CommandCategory | None = None,
        logger: logging.Logger,
        is_script: bool = False,
    ) -> Command:
        """
        Wraps the provided pipeline assembled command using the defined wrapper.

        If a wrapper is defined, it applies the wrapper function to the pipeline
        assembled command. Otherwise, it concatenates the command and the pipeline
        assembled command.

        Args:
            pipeline_assembled_command (Command): The assembled command to be wrapped.
            parameter (T): Context object forwarded to the wrapper callable (e.g.
                the runtime configuration).
            command_category (CommandCategory | None): Category of the command
                being wrapped; the wrapper is skipped unless this is in
                `applies_for` (defaulting to `[CommandCategory.GAME]`).
            logger (logging.Logger): Logger used to log the wrapped command.
            is_script (bool): Whether the pipeline is being assembled for a
                script context; the wrapper is skipped unless `use_in_script`
                is True.

        Returns:
            Command: The wrapped command, or the original command unchanged if
            the wrapper doesn't apply for this category/context.
        """
        # If no specific command category is provided, default to applying for GAME category only.
        applies_for_with_default = self.applies_for or [CommandCategory.GAME]
        if not (command_category and command_category in applies_for_with_default):
            # If the wrapper does not apply for the given command category,
            # return the original command.
            return pipeline_assembled_command
        if is_script and not self.use_in_script:
            return pipeline_assembled_command

        wrapped_command = self.wrapper(pipeline_assembled_command, parameter)
        logger.debug(
            "Wrapped command build step: %s", wrapped_command.get_full_command()
        )
        return wrapped_command
