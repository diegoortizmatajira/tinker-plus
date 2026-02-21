"""
Defines the ExecutableCommand class, which represents a command that can be
executed with optional arguments and category.
"""

from dataclasses import dataclass
from enum import StrEnum
import os
import shlex
from typing import Self, cast


class CommandCategory(StrEnum):
    """
    Represents the category of a command
    """

    TRAINER = "trainer"
    GAME = "game"
    COMPATIBILITY_TOOL = "compatibility_tool"
    SCRIPT = "script"


@dataclass
class Command:
    """
    Represents a command that can be executed with optional arguments and category.
    """

    internal_representation: list["str | Command"]
    cwd: str | None = None
    category: CommandCategory | None = None

    @classmethod
    def from_parts(
        cls,
        command_str: str,
        args_str: str | None = None,
        *,
        cwd: str | None = None,
        category: CommandCategory | None = None,
    ):
        """
        Creates a Command instance from a command string and an optional arguments string.
        Args:
            command_str (str): The command string to create the Command instance from.
            args_str (str | None): An optional string of arguments to include
            in the Command instance.
            category (CommandCategory | None): Optional category for the command.
        Returns:
            Command: A Command instance representing the provided command string and arguments.
        """
        return cls(
            [command_str]
            + cast(list["str|Command"], (shlex.split(args_str) if args_str else [])),
            cwd=cwd,
            category=category,
        )

    @classmethod
    def from_string(
        cls,
        command_str: str,
        args_str: str | None = None,
        *,
        cwd: str | None = None,
        category: CommandCategory | None = None,
    ) -> Self:
        """
        Creates a Command instance from a command string.

        Args:
            command_str (str): The command string to create the Command instance from.
            category (CommandCategory | None): Optional category for the command.
        Returns:
            Command: A Command instance representing the provided command string.
        """
        return cls(
            internal_representation=cast(
                list["str|Command"],
                shlex.split(command_str + ((" " + args_str) if args_str else "")),
            ),
            cwd=cwd,
            category=category,
        )

    @property
    def command(self) -> str:
        """
        Returns the command string.

        Returns:
            str: The command string.
        """
        if len(self.internal_representation) == 0:
            raise ValueError("Command cannot be empty.")

        if isinstance(self.internal_representation[0], Command):
            return self.internal_representation[0].command
        return self.internal_representation[0]

    def get_full_command(self) -> str:
        """
        Constructs the full command string by combining the command and its arguments.
        Returns:
            str: The full command string.
        """
        chain_command = self.get_chain_command()
        return " ".join(
            [f'"{part}"' if " " in part else part for part in chain_command]
        )

    def get_chain_command(self) -> list[str]:
        """
        Constructs a list of command components for execution, including the
        command and its arguments.

        Returns:
            list[str]: A list of command components.
        """
        result = []
        if self.internal_representation:
            for arg in self.internal_representation:
                if isinstance(arg, Command):
                    result.extend(arg.get_chain_command())
                else:
                    part = arg
                    if os.path.isabs(part):
                        # Resolve absolute paths to their real path to handle
                        # symlinks and ensure correct execution
                        part = os.path.realpath(part)
                    result.append(part)
        return result

    def replace_command(self, new_command_str: str):
        """
        Replaces the command string with a new command string.

        Args:
            new_command_str (str): The new command string to replace the existing command.

        Returns:
            Command: A new Command instance with the updated command string.
        """
        if not self.internal_representation:
            raise ValueError("Cannot replace command in an empty Command instance.")

        new_internal_representation = self.internal_representation.copy()
        if isinstance(new_internal_representation[0], Command):
            new_internal_representation[0].replace_command(new_command_str)
        else:
            new_internal_representation[0] = new_command_str
        self.internal_representation = new_internal_representation

    def replace_args(self, new_args_str: str):
        """
        Replaces the arguments of the command with new arguments.

        Args:
            new_args_str (str): The new arguments string to replace the existing arguments.

        Returns:
            Command: A new Command instance with the updated arguments.
        """
        if not self.internal_representation:
            raise ValueError("Cannot replace arguments in an empty Command instance.")

        new_internal_representation = self.internal_representation.copy()
        if isinstance(new_internal_representation[0], Command):
            new_internal_representation[0].replace_args(new_args_str)
        else:
            # Replace all arguments except the command itself
            new_internal_representation = [new_internal_representation[0]] + (
                shlex.split(new_args_str) if new_args_str else []
            )
        self.internal_representation = cast(
            list[str | Command], new_internal_representation
        )
