"""Defines the Runtime configuration for the application."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
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
    of runtime behavior such as the compatibility tool (Proton) in use, forked/trainer
    commands, pipeline wrappers, and the Wine prefix path.

    Attributes:
        original_command (Sequence[str]): The original command line as received from Steam.
        game_info (GameInfo): Information about the game being launched.
        steam_environment_data (SteamEnvironmentData): Parsed Steam environment data.
        dry_run (bool): If True, no side effects are performed; actions are only logged.
        steam_compatibility_tool (str | None): Name of the selected compatibility tool (Proton).
        steam_compatibility_tools_path (str | None): Path to the compatibility tools directory.
        game_executable_command (Command | None): The main game executable command.
        wine (str | None): Path to the Wine executable for the selected compatibility tool.
        fork_commands (list[Command] | None): Additional commands (e.g. trainers) to fork.
        prefix_path (str | None): The path to the Wine prefix.
        execute_trainers (bool): Whether forked trainer commands should be executed.
        execute_forks_only (bool): If True, only forked commands run, skipping the main game.
        environment_variables (dict[str, str] | None): Environment variables to apply.
        pipeline_wrappers (list[CommandWrapper[Self]] | None): Wrappers applied to build
            the final command pipeline (e.g. GameMode, Proton, Steam runtime).
        log_executable_commands (bool): Whether each executed command is logged to its own file.
        loaded_global_configuration (ConfigurationDictionary | None): Snapshot of the
            merged global configuration, used to compute per-game config diffs.
        external_terminal_command_template (list[str] | None): Template used to launch
            commands in an external terminal.
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

    def set_debugger(self, command: Command) -> None:
        """
        Sets the debugger command in the current configuration.

        Args:
            command (ExecutableCommand): The debugger command to be set.
        """
        trainer_path = Path(command.command)
        self.set_environment_variable(
            "PROTON_REMOTE_DEBUG_CMD", command.get_full_command()
        )
        self.set_environment_variable(
            "PRESSURE_VESSEL_FILESYSTEMS_RW", trainer_path.parent.resolve().as_posix()
        )

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
