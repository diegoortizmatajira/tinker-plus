"""
Defines the ExecutableCommand class, which represents a command that can be
executed with optional arguments and category.
"""

from dataclasses import dataclass
from enum import StrEnum


class CommandCategory(StrEnum):
    """
    Represents the category of a command
    """

    TRAINER = "trainer"
    GAME = "game"
    COMPATIBILITY_TOOL = "compatibility_tool"


@dataclass
class Command:
    """
    Represents a command that can be executed with optional arguments and category.
    """

    command: str
    args: str | None = None
    cwd: str | None = None
    category: CommandCategory | None = None

    def get_full_command(self) -> str:
        """
        Constructs the full command string by combining the command and its arguments.
        Returns:
            str: The full command string.
        """
        quoted_command = f'"{self.command}"' if " " in self.command else self.command
        if self.args:
            return f"{quoted_command} {self.args}".strip()
        return quoted_command.strip()
