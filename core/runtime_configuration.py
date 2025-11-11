from dataclasses import dataclass
from typing import List, Optional

COMMAND_TRAINER = "trainer"
COMMAND_GAME = "game"


@dataclass
@dataclass
class ExecutableCommand:
    """
    Represents a command that can be executed with optional arguments and category.

    Attributes:
        command (str): The command to execute.
        args (Optional[str]): Optional arguments for the command.
        category (Optional[str]): An optional category to classify the command.
    """

    command: str
    args: Optional[str]
    category: Optional[str] = None
    command: str
    args: Optional[str]
    category: Optional[str] = None


@dataclass
class RuntimeConfiguration:
    """
    Represents the runtime configuration for the application, allowing customization
    of runtime behavior such as the use of Proton, forked commands, winetricks,
    and the prefix path.

    Attributes:
        use_proton (str): Specifies whether Proton is used. Defaults to an empty string.
        fork_commands (Optional[List[ExecutableCommand]]): A list of forked commands to execute.
        command (str): The primary command to execute. Defaults to an empty string.
        winetricks (Optional[List[str]]): A list of winetricks to apply. Defaults to None.
        prefix_path (str): The path to the runtime prefix. Defaults to an empty string.
    """

    steam_app_id: str = ""
    steam_game_id: str = ""
    steam_compat_install_path: str = ""
    steam_compat_data_path: str = ""
    use_proton: str = ""
    fork_commands: Optional[List[ExecutableCommand]] = None
    command: str = ""
    winetricks: Optional[List[str]] = None
    prefix_path: str = ""
    execute_trainers: bool = True

    @property
    def has_trainers(self) -> bool:
        """
        Checks if there are any forked commands categorized as trainers.

        Returns:
            bool: True if there is at least one trainer command, False otherwise.
        """
        if self.fork_commands is None:
            return False
        for cmd in self.fork_commands:
            if cmd.category == COMMAND_TRAINER:
                return True
        return False

    def add_winetricks(self, tricks: List[str]) -> None:
        """
        Adds a list of winetricks to the current configuration.

        Args:
            tricks (List[str]): A list of winetricks to be added. Duplicates
            will be avoided, and an empty list will initialize the winetricks
            list if it is currently None.
        """
        if self.winetricks is None:
            self.winetricks = []
        for trick in tricks:
            # Avoid duplicates
            if trick not in self.winetricks:
                self.winetricks.append(trick)

    def add_fork_command(self, command: ExecutableCommand) -> None:
        """
        Adds a forked command to the current configuration.

        Args:
            command (ExecutableCommand): The command to be added. An empty
            list will initialize the fork_commands list if it is currently None.
        """
        if self.fork_commands is None:
            self.fork_commands = []
        self.fork_commands.append(command)
