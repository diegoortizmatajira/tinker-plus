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

    original_command: List[str]
    dry_run: bool= False
    steam_app_id: Optional[str] = None
    steam_game_id: Optional[str] = None
    steam_compat_install_path: Optional[str] = None
    steam_compat_data_path: Optional[str] = None
    steam_wrapper: Optional[str] = None
    steam_reaper: Optional[str] = None
    steam_sniper: Optional[str] = None
    steam_compatibility_command: Optional[str] = None
    steam_compatibility_tool: Optional[str] = None
    steam_compatibility_tools_path: Optional[str] = None
    steam_game_exe: Optional[str] = None
    steam_other_wrapper_commands: Optional[str] = None
    use_proton: Optional[str] = None
    fork_commands: Optional[List[ExecutableCommand]] = None
    winetricks: Optional[List[str]] = None
    prefix_path: Optional[str] = None
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
            if trick != "" and trick not in self.winetricks:
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
