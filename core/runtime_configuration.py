"""Defines the Runtime configuration for the application."""

from dataclasses import dataclass
import logging
from typing import Callable, List, Optional

from core.game_info import GameInfo


COMMAND_TRAINER = "trainer"
COMMAND_GAME = "game"


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

    command: Optional[str] = None
    wrapper: Optional[Callable[[str, "RuntimeConfiguration"], str]] = None
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
        fork_commands (Optional[List[ExecutableCommand]]): A list of forked commands to execute.
        command (str): The primary command to execute. Defaults to an empty string.
        winetricks (Optional[List[str]]): A list of winetricks to apply. Defaults to None.
        prefix_path (str): The path to the runtime prefix. Defaults to an empty string.
    """

    original_command: List[str]
    game_info: GameInfo
    dry_run: bool = False
    steam_app_id: Optional[str] = None
    steam_game_id: Optional[str] = None
    steam_base_folder: Optional[str] = None
    steam_compat_install_path: Optional[str] = None
    steam_compat_data_path: Optional[str] = None
    steam_wrapper: Optional[str] = None
    steam_reaper: Optional[str] = None
    steam_sniper: Optional[str] = None
    steam_compatibility_command: Optional[str] = None
    steam_compatibility_tool: Optional[str] = None
    steam_compatibility_tools_path: Optional[str] = None
    steam_game_exe: Optional[str] = None
    steam_game_args: Optional[str] = None
    wine: Optional[str] = None
    fork_commands: Optional[List[ExecutableCommand]] = None
    install_winetricks: bool = True
    winetricks: Optional[List[str]] = None
    prefix_path: Optional[str] = None
    execute_trainers: bool = True
    execute_forks_only: bool = False
    environment_variables: Optional[dict[str, str]] = None
    pipeline_wrappers: Optional[List[PipelineWrapper]] = None

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

    def reset(self) -> None:
        """
        Resets the runtime configuration to its default state.
        """
        self.fork_commands = None
        self.winetricks = None
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
