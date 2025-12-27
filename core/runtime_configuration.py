"""Defines the Runtime configuration for the application."""

from collections.abc import Sequence
from dataclasses import dataclass
import logging
from typing import Callable

from core.configuration_types import ConfigurationDictionary
from core.game_info import GameInfo
from core.steam_environment_data import SteamEnvironmentData


COMMAND_TRAINER = "trainer"
COMMAND_GAME = "game"


@dataclass
class ExecutableCommand:
    """
    Represents a command that can be executed with optional arguments and category.

    Attributes:
        command (str): The command to execute.
        args (str | None): Optional arguments for the command.
        category (str | None): An optional category to classify the command.
    """

    command: str
    args: str | None = None
    category: str | None = None

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


@dataclass()
class PipelineWrapper:
    """
    Represents a pipeline wrapper with environment variables and a command to execute.
    Attributes:
        environment_variables (dict[str, str]): A dictionary of environment variables to set.
        command (str): The command to execute within the pipeline wrapper.
    """

    command: str | None = None
    wrapper: Callable[[str, "RuntimeConfiguration"], str] | None = None
    is_global_wrapper: bool = True
    is_fork_wrapper: bool = False

    def wrap(
        self,
        pipeline_assembled_command: str,
        runtime_configuration: "RuntimeConfiguration",
        *,
        is_global: bool = True,
        is_fork: bool = False,
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
        if is_global != self.is_global_wrapper:
            return pipeline_assembled_command
        if is_fork and not self.is_fork_wrapper:
            return pipeline_assembled_command

        if self.wrapper:
            wrapped_command = self.wrapper(
                pipeline_assembled_command, runtime_configuration
            )
        else:
            wrapped_command = f"{self.command} {pipeline_assembled_command}"
        logger.debug("Wrapped command build step: %s", wrapped_command)
        return wrapped_command


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
    steam_wrapper: str | None = None
    steam_reaper: str | None = None
    steam_sniper: str | None = None
    steam_compatibility_command: str | None = None
    steam_compatibility_tool: str | None = None
    steam_compatibility_tools_path: str | None = None
    steam_game_exe: str | None = None
    steam_game_args: str | None = None
    steam_game_cwd: str | None = None
    wine: str | None = None
    fork_commands: list[ExecutableCommand] | None = None
    prefix_path: str | None = None
    execute_trainers: bool = True
    execute_forks_only: bool = False
    environment_variables: dict[str, str] | None = None
    pipeline_wrappers: list[PipelineWrapper] | None = None
    log_executable_commands: bool = False
    loaded_global_configuration: ConfigurationDictionary | None = None

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
            dry_run=True,
        )

    def get_game_identifier(self) -> str:
        """
        Retrieves the game identifier from the steam environment data.

        Returns:
            str: The game identifier.
        """
        return (
            self.steam_environment_data.steam_game_id
            or self.steam_environment_data.steam_app_id
            or "unknown"
        )

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
            if cmd.category == COMMAND_TRAINER:
                return True
        return False

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

    def add_pipeline_wrapper(self, wrapper: PipelineWrapper) -> None:
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
