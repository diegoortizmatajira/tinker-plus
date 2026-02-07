"""Defines the Runtime configuration for the application."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Self

from .command import Command, CommandCategory
from .command_wrapper import CommandWrapper
from .configuration_types import ConfigurationDictionary
from .game_info import GameInfo
from .steam_environment_data import SteamEnvironmentData


# pylint: disable=too-many-instance-attributes
@dataclass
class RuntimeConfiguration:
    """
    Represents the runtime configuration for the application, allowing customization
    of runtime behavior such as the use of Proton, forked commands, winetricks,
    and the prefix path.

    Attributes:
        use_proton (str): Specifies whether Proton is used. Defaults to an empty string.
        fork_commands (list[ExecutableCommand] | None): A list of forked commands to execute.
        command (str): The primary command to execute. Defaults to an empty string.
        winetricks (list[str] | None): A list of winetricks to apply. Defaults to None.
        prefix_path (str): The path to the runtime prefix. Defaults to an empty string.
    """

    original_command: Sequence[str]
    game_info: GameInfo
    steam_environment_data: SteamEnvironmentData
    dry_run: bool = False
    steam_compatibility_command: str | None = None
    steam_compatibility_tool: str | None = None
    steam_compatibility_tools_path: str | None = None
    game_executable_command: Command | None = None
    game_executable_wrapper: CommandWrapper[Self] | None = None
    wine: str | None = None
    fork_commands: list[Command] | None = None
    prefix_path: str | None = None
    execute_trainers: bool = True
    execute_forks_only: bool = False
    environment_variables: dict[str, str] | None = None
    pipeline_wrappers: list[CommandWrapper[Self]] | None = None
    log_executable_commands: bool = False
    loaded_global_configuration: ConfigurationDictionary | None = None
    external_terminal_command_template: list[str] | None = None

    @staticmethod
    def empty() -> "RuntimeConfiguration":
        """
        Creates an empty RuntimeConfiguration instance with default values.

        Returns:
            RuntimeConfiguration: An instance of RuntimeConfiguration with default values.
        """
        return RuntimeConfiguration(
            original_command=[],
            game_info=GameInfo.empty(),
            steam_environment_data=SteamEnvironmentData.empty(),
            dry_run=True,
        )

    def get_game_identifier(self) -> str:
        """
        Retrieves the game identifier

        Returns:
            str: The game identifier.
        """
        return (
            self.steam_environment_data.steam_game_id
            or self.steam_environment_data.steam_app_id
            or "unknown"
        )

    def get_game_files_path(self) -> str | None:
        """
        Retrieves the path to the game files.

        Returns:
            str | None: The path to the game files, or None if not available.
        """
        return self.steam_environment_data.steam_compat_install_path

    def get_compat_data_path(self) -> str | None:
        """
        Retrieves the path to the runtime prefix.

        Returns:
            str | None: The path to the runtime prefix, or None if not set.
        """
        return self.steam_environment_data.steam_compat_data_path

    def reset(self) -> None:
        """
        Resets the runtime configuration to its default state.
        """
        self.fork_commands = None
        self.execute_trainers = True
        self.environment_variables = None
        self.pipeline_wrappers = None

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
            if cmd.category is CommandCategory.TRAINER:
                return True
        return False

    def add_fork_command(self, command: Command) -> None:
        """
        Adds a forked command to the current configuration.

        Args:
            command (ExecutableCommand): The command to be added. An empty
            list will initialize the fork_commands list if it is currently None.
        """
        if self.fork_commands is None:
            self.fork_commands = []
        self.fork_commands.append(command)

    def set_environment_variable(self, key: str, value: str) -> None:
        """
        Sets an environment variable in the current configuration.

        Args:
            key (str): The environment variable key.
            value (str): The environment variable value.
        """
        if self.environment_variables is None:
            self.environment_variables = {}
        self.environment_variables[key] = value

    def add_pipeline_wrapper(self, wrapper: CommandWrapper[Self]) -> None:
        """
        Adds a pipeline wrapper to the current configuration. Each wrapper
        will affect the final command in the order they were added.

        Args:
            wrapper (PipelineWrapper): The pipeline wrapper to be added. An empty
            list will initialize the pipeline_wrappers list if it is currently None.
        """
        if self.pipeline_wrappers is None:
            self.pipeline_wrappers = []
        self.pipeline_wrappers.append(wrapper)
