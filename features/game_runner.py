"""
A feature provider for executing the main game command and any forked commands
"""

import os
import stat
from subprocess import Popen
import tempfile
from time import sleep
from typing import Any, override

from core import (
    FeatureProvider,
    ProcessRunner,
)
from defaults import CWD_DIR_NAME
from model import (
    Command,
    CommandCategory,
    RuntimeConfiguration,
    ConfigurationProperty,
    ConfigurationDictionary,
)

GAME_CUSTOM_EXE_PROPERTY = ConfigurationProperty(
    str,
    "GAME_CUSTOM_EXE",
    "Custom Game Executable",
    "Allows specifying the main game executable to run.",
    None,
)
GAME_CUSTOM_ARGS_PROPERTY = ConfigurationProperty(
    str,
    "GAME_CUSTOM_ARGS",
    "Custom Game Arguments",
    "Allows specifying additional arguments for the game executable.",
    None,
)
GAME_CUSTOM_CWD_PROPERTY = ConfigurationProperty(
    str,
    "GAME_CUSTOM_CWD",
    "Custom Game Working Directory",
    "Allows specifying a custom working directory for the game executable.",
    None,
)
GAME_RUN_FORKS_ONLY_PROPERTY = ConfigurationProperty(
    bool,
    "GAME_RUN_FORKS_ONLY",
    "Run Forked Commands Only",
    "If set to 'True', only the forked commands will be executed, skipping "
    + "the main game command.",
    default=False,
)
GAME_RUN_WITH_SCRIPT_PROPERTY = ConfigurationProperty(
    bool,
    "GAME_RUN_WITH_SCRIPT",
    "Run Commands with Script",
    "If set to 'True', commands will be executed through a temporary "
    + "script to ensure proper sequencing and environment setup.",
    default=True,
)

SLEEP_TIME_BETWEEN_COMMANDS = 2  # seconds


class GameRunner(FeatureProvider):
    """
    A feature provider for executing the main game command and any forked
    commands using the runtime configuration.
    """

    run_with_script: bool = True
    game_process: Popen[Any] | None = None
    trainer_process_list: list[Popen[Any]] = []
    wait_for_forked_processes: bool = False

    def __init__(self):
        super().__init__(
            "Game Runner",
            [
                GAME_CUSTOM_EXE_PROPERTY,
                GAME_CUSTOM_ARGS_PROPERTY,
                GAME_CUSTOM_CWD_PROPERTY,
                GAME_RUN_FORKS_ONLY_PROPERTY,
                GAME_RUN_WITH_SCRIPT_PROPERTY,
            ],
            "Game Execution",
        )

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        """Builds the game executable command from configuration overrides
        (custom executable, arguments, working directory) and records whether
        commands should run via a temporary script."""
        runtime_configuration.execute_forks_only = GAME_RUN_FORKS_ONLY_PROPERTY.get(
            configuration, False
        )
        if runtime_configuration.execute_forks_only:
            self.logger.info(
                "Configured to run only forked commands, skipping main game."
            )
        if not runtime_configuration.game_executable_command:
            runtime_configuration.game_executable_command = Command.from_string(
                "echo", category=CommandCategory.GAME
            )

        custom_exe = GAME_CUSTOM_EXE_PROPERTY.get(configuration)
        if custom_exe:
            runtime_configuration.game_executable_command.replace_command(custom_exe)
            self.logger.info("Using custom game executable: %s", custom_exe)

        custom_args = GAME_CUSTOM_ARGS_PROPERTY.get(configuration)
        if custom_args:
            runtime_configuration.game_executable_command.replace_args(custom_args)
            self.logger.info("Using custom game arguments: %s", custom_args)
        custom_cwd = GAME_CUSTOM_CWD_PROPERTY.get(configuration)
        runtime_configuration.game_executable_command.cwd = (
            custom_cwd
            or runtime_configuration.steam_environment_data.steam_compat_install_path
            or f"{runtime_configuration.prefix_path}/{CWD_DIR_NAME}"
        )
        self.logger.info(
            "Using game working directory: %s",
            runtime_configuration.game_executable_command.cwd,
        )

        self.run_with_script = GAME_RUN_WITH_SCRIPT_PROPERTY.get_or_fail(configuration)

        return runtime_configuration

    def get_run_sequence(
        self,
        sequence: list[CommandCategory],
        runtime_configuration: RuntimeConfiguration,
    ) -> list[Command]:
        """
        Returns an ordered list of commands to execute based on the runtime configuration.
        """

        def filter_per_category(category: CommandCategory) -> list[Command]:
            if category == CommandCategory.GAME:
                if (
                    runtime_configuration.game_executable_command
                    and not runtime_configuration.execute_forks_only
                ):
                    return [runtime_configuration.game_executable_command]
                return []
            if (
                category == CommandCategory.TRAINER
                and not runtime_configuration.execute_trainers
            ):
                # If trainers are not to be executed, return an empty list for the trainer category
                return []
            return [
                cmd
                for cmd in runtime_configuration.fork_commands or []
                if cmd.category == category
            ]

        ordered_commands = []
        for category in sequence:
            # Add commands of the current category to the ordered list
            ordered_commands.extend(filter_per_category(category))
        return ordered_commands

    def run_game(
        self,
        runtime_configuration: RuntimeConfiguration,
        command: Command,
    ):
        """Launches the main game command through the pipeline and stores its
        process handle, raising RuntimeError if the launch fails.

        Args:
            runtime_configuration (RuntimeConfiguration): The runtime configuration
            used to build and launch the command.
            command (Command): The game command to launch.
        """
        self.game_process = ProcessRunner.run_with_pipeline(
            command,
            runtime_configuration,
            self.logger,
        )
        if self.game_process:
            self.logger.info("Launched game with PID: %s", self.game_process.pid)
        else:
            self.logger.error("Failed to launch the game process.")
            raise RuntimeError("Failed to launch the game process.")

    def run_trainer(
        self,
        runtime_configuration: RuntimeConfiguration,
        command: Command,
    ):
        """Launches a forked trainer command through the pipeline and appends
        its process handle to `trainer_process_list`.

        Args:
            runtime_configuration (RuntimeConfiguration): The runtime configuration
            used to build and launch the command.
            command (Command): The trainer command to launch.
        """
        sleep(5)
        # Small delay to ensure trainers launch after the game process has started
        self.logger.info(
            "Preparing trainer command '%s'",
            command.command,
        )
        fork_process = ProcessRunner.run_with_pipeline(
            command,
            runtime_configuration,
            self.logger,
            # custom_environment_variables=SteamUtil.get_anonymous_steam_overrides(),
        )
        if fork_process:
            self.trainer_process_list.append(fork_process)
            self.logger.info(
                "Trainer command '%s' launched with PID: %s",
                command.command,
                fork_process.pid,
            )
            sleep(2)

    def execute_with_script(
        self,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        """
        Executes the commands in the pipeline using a temporary script.

        This method generates a temporary shell script to execute the runtime
        configuration's command sequence in the specified order. Each command in
        the sequence is executed with a delay between them to ensure proper
        sequencing and environment setup.

        Args:
            _configuration (ConfigurationDictionary): The configuration dictionary.
            runtime_configuration (RuntimeConfiguration): The runtime configuration
                containing the command sequence and other relevant settings.
        """
        sequence = self.get_run_sequence(
            [
                CommandCategory.TRAINER,
                CommandCategory.GAME,
            ],
            runtime_configuration,
        )
        script_commands = [
            ProcessRunner.assemble_command_str(
                command,
                runtime_configuration,
                self.logger,
                is_script=True,
            ).get_full_command()
            for command in sequence
        ]
        if not script_commands:
            self.logger.error(
                "No commands to execute (no game or trainer commands were configured)."
            )
            raise RuntimeError("No commands available to build the execution script.")
        if len(script_commands) > 1:
            script_path: str
            with tempfile.NamedTemporaryFile(delete=False, suffix=".sh") as tmp:
                script_path = tmp.name
                tmp.write(b"#!/bin/bash\n")

                tmp.write(
                    f" & \nsleep {SLEEP_TIME_BETWEEN_COMMANDS}\n".join(
                        # " & \n".join(
                        script_commands
                    ).encode("utf-8")
                )

            self.logger.info("Created temporary script at: %s", script_path)
            # Make it executable
            os.chmod(script_path, os.stat(script_path).st_mode | stat.S_IEXEC)
            script_command = Command.from_string(
                script_path, category=CommandCategory.SCRIPT
            )
        else:
            # If there's only one command, we can run it directly without a script
            script_command = Command.from_string(
                script_commands[0], category=CommandCategory.SCRIPT
            )
        # Run the script which will execute the commands in sequence
        self.game_process = ProcessRunner.run_with_pipeline(
            script_command, runtime_configuration, self.logger
        )

    @override
    def execute_in_pipeline(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        self.trainer_process_list = []
        self.game_process = None
        if self.run_with_script:
            # create a temporary script to execute the commands in sequence
            return self.execute_with_script(configuration, runtime_configuration)

        # Execute commands directly without using a temporary script
        sequence = self.get_run_sequence(
            [
                CommandCategory.GAME,
                CommandCategory.TRAINER,
            ],
            runtime_configuration,
        )
        for command in sequence:
            if command.category == CommandCategory.GAME:
                self.run_game(runtime_configuration, command)
            elif command.category == CommandCategory.TRAINER:
                self.run_trainer(runtime_configuration, command)

    @override
    def wait_for_completion(
        self,
        _configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ):
        if self.game_process:
            # Wait for the game process to exit if it's still running
            with self.game_process:
                result = self.game_process.wait()
                self.logger.info("Game process exited with return code: %s", result)

        wait_for_trainers = True

        for fork_process in self.trainer_process_list:
            status = fork_process.poll()
            if status is None:
                if wait_for_trainers:
                    self.logger.info(
                        "Waiting for trainer process with PID %s to exit...",
                        fork_process.pid,
                    )
                    result = fork_process.wait()
                    self.logger.info(
                        "Trainer process with PID %s exited with code: %s",
                        fork_process.pid,
                        result,
                    )
                else:
                    self.logger.info(
                        "Terminating trainer process with PID %s...", fork_process.pid
                    )
                    fork_process.terminate()
            else:
                self.logger.info(
                    "Trainer process with PID %s has already exited with code: %s",
                    fork_process.pid,
                    status,
                )
                # Log stderr if the trainer failed
                if status != 0:
                    stderr_output = (
                        fork_process.stderr.read().decode(errors="replace")
                        if fork_process.stderr
                        else ""
                    )
                    if stderr_output:
                        self.logger.error(
                            "Trainer stderr output:\n%s", stderr_output.strip()
                        )
