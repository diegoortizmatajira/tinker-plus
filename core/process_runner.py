"""Module for running processes with compatibility tools and handling execution pipelines."""

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, final, overload

from model import (
    Command,
    CommandCategory,
    CommandWrapper,
    RuntimeConfiguration,
)

from defaults import (
    LOG_DRY_RUN,
    LOG_EXECUTING,
)
from .log_storage import LogFactory


@final
class ProcessRunner:
    """
    Utility class for running processes with compatibility tools and handling execution pipelines.
    """

    @overload
    @staticmethod
    def run_in_wine_prefix(
        exe_command: Command,
        runtime_configuration: RuntimeConfiguration,
        logger: logging.Logger,
    ) -> bool:
        """
        Executes the given command in a Wine prefix environment.

        This function sets the necessary environment variables for Wine,
        constructs the command with optional logging or dry-run behaviors,
        and executes it using the subprocess module. The execution can also
        capture output if explicitly enabled.

        Arguments:
            exe_command (ExecutableCommand): The command to be executed.
            runtime_configuration (RuntimeConfiguration): The runtime configuration
                containing Wine-related settings, environment variables, and execution
                options such as logging and dry-run.
            logger (logging.Logger): Logger instance for logging messages, including
                command execution details and errors.

        Returns:
            bool: True if the command executes successfully

        Raises:
            RuntimeError: If the WINEPREFIX environment variable is not set or if the command
            execution fails due to unhandled errors.
        """

    @overload
    @staticmethod
    def run_in_wine_prefix(
        exe_command: Command,
        runtime_configuration: RuntimeConfiguration,
        logger: logging.Logger,
        capture_output: bool,
    ) -> tuple[bool, str]:
        """
        Executes the given command in a Wine prefix environment.

        This function sets up the necessary environment variables for Wine,
        constructs the command with optional logging or dry-run behaviors, and
        executes it using the subprocess module. It can also capture output if this
        option is explicitly enabled.

        Args:
            exe_command (ExecutableCommand): The command to be executed in the Wine
                environment.
            runtime_configuration (RuntimeConfiguration): Configuration specifying
                environment variables, Wine path, and other execution details.
            logger (logging.Logger): Instance used for logging execution details.
            capture_output bool: Whether to capture the command's
                standard output. If True, the output is captured and returned along
                with the execution status.

        Returns:
            tuple[bool, str]: returns a boolean indicating whether the command
            executed successfully. If `capture_output` is True, returns a tuple
            (success, output) where the output is the captured command output as a
            string.

        Raises:
            RuntimeError: If the WINEPREFIX is not properly set or command execution fails.
        """

    @staticmethod
    def run_in_wine_prefix(
        exe_command: Command,
        runtime_configuration: RuntimeConfiguration,
        logger: logging.Logger,
        capture_output: bool | None = None,
    ) -> bool | tuple[bool, str]:
        """
        Executes the given command in a Wine prefix environment.

        This function sets the necessary environment variables for Wine,
        constructs the command with optional logging or dry-run behaviors,
        and executes it using the subprocess module. The execution can also
        capture output if explicitly enabled.

        Args:
            exe_command (ExecutableCommand): The command to be executed.
            runtime_configuration (RuntimeConfiguration): The runtime configuration
                containing Wine-related settings and environment variables.
            logger (logging.Logger): Logger instance for logging messages.
            capture_output (bool | None, optional): Whether to capture the command's output.
                If not specified, the output won't be captured. Defaults to None.

        Returns:
            bool | tuple[bool, str]: True if the command executes successfully, or
            (True, captured_output) if output capturing is enabled. False otherwise.

        Raises:
            RuntimeError: If the WINEPREFIX variable is not set, or if the command
            execution fails.
        """
        wine_prefix = runtime_configuration.prefix_path
        if not wine_prefix:
            raise RuntimeError("WINEPREFIX environment variable is not set.")

        environment_variables = os.environ.copy()
        environment_variables.update(runtime_configuration.environment_variables or {})
        environment_variables["WINEPREFIX"] = wine_prefix
        logger.info("Using  WINEPREFIX=%s", wine_prefix)
        if runtime_configuration.wine:
            environment_variables["WINE"] = runtime_configuration.wine
            logger.info("Using  WINE=%s", runtime_configuration.wine)

        command = f"{exe_command.get_full_command()}"
        if runtime_configuration.log_executable_commands:
            exe_path = Path(exe_command.command)
            log_file = LogFactory.singleton().get_log_filename(f"{exe_path.stem}.log")
            command += f" >> {log_file}"
        if runtime_configuration.dry_run:
            logger.info(
                LOG_DRY_RUN.format("Would execute command in Wine prefix: %s"), command
            )
            if capture_output is None:
                return True
            return True, "win10"
        try:
            logger.info(
                LOG_EXECUTING.format("Executing command in Wine prefix: %s"), command
            )
            result = subprocess.run(
                command,
                env=environment_variables,
                shell=True,
                check=True,
                capture_output=capture_output or False,
                text=capture_output,
            )
            if result.returncode != 0:
                logger.error(
                    "Command '%s' exited with non-zero return code: %s",
                    command,
                    result.returncode,
                )
            else:
                logger.debug(
                    "Command '%s' executed successfully with return code: %s",
                    command,
                    result.returncode,
                )
            if capture_output is None:
                return result.returncode == 0
            return result.returncode == 0, result.stdout
        except Exception as e:
            logger.error("Error while running command in Wine prefix: %s", e)
            raise RuntimeError(
                f"Error executing command in Wine prefix: '{exe_command}'"
            ) from e

    @staticmethod
    def wait_and_log(
        process: subprocess.Popen[Any],
        logger: logging.Logger,
        label: str,
    ) -> int:
        """
        Waits for the given process to exit, logging its PID and exit code.

        Args:
            process (subprocess.Popen): The process to wait for.
            logger (logging.Logger): Logger instance used for the launch/exit messages.
            label (str): Human-readable label for the process, used in the log
                messages (e.g. "before startup process").

        Returns:
            int: The process's exit code.
        """
        with process:
            logger.info("Launched '%s' with PID: %s", label, process.pid)
            result = process.wait()
            logger.info("'%s' exited with return code: %s", label.capitalize(), result)
            return result

    @staticmethod
    def assemble_command_str(
        command: Command,
        runtime_configuration: RuntimeConfiguration,
        logger: logging.Logger,
        override_log_to_file: bool | None = None,
        override_command_category: CommandCategory | None = None,
        is_script: bool = False,
    ) -> Command:
        """
        Assembles the full command string with optional logging to file based
        on the runtime configuration.
        """
        actual_command = command
        logger.debug(
            "Available pipeline wrappers: %d",
            len(runtime_configuration.pipeline_wrappers or []),
        )
        # Takes the pipeline wrappers in reverse order
        for wrapper in reversed(runtime_configuration.pipeline_wrappers or []):
            actual_command = wrapper.wrap(
                actual_command,
                runtime_configuration,
                command_category=override_command_category or command.category,
                logger=logger,
                is_script=is_script,
            )

        # TODO: Consider if we want to log the final assembled command or the original command, or both.
        # if runtime_configuration.log_executable_commands and (
        #     override_log_to_file is not False
        # ):
        #     exe_path = Path(command.command)
        #     log_file = LogFactory.singleton().get_log_filename(f"{exe_path.stem}.log")
        #     actual_command = Command([actual_command, ">>", log_file, "2>&1"])
        return actual_command

    @classmethod
    def run_command_with_compatibility_tool(
        cls,
        exe_command: Command,
        runtime_configuration: RuntimeConfiguration,
        logger: logging.Logger,
    ) -> bool:
        """
        Executes a given command using a compatibility tool defined in the runtime configuration.

        Args:
            exe_command (Command): The command to execute.
            runtime_configuration (RuntimeConfiguration): The runtime configuration
                providing the pipeline wrappers and environment variables to apply.
            logger (logging.Logger): Logger instance for logging execution details.
        """

        environment_variables = os.environ.copy()
        environment_variables.update(runtime_configuration.environment_variables or {})
        command = cls.assemble_command_str(exe_command, runtime_configuration, logger)
        if runtime_configuration.dry_run:
            logger.info(LOG_DRY_RUN.format("Would execute command: %s"), command)
            return True
        try:
            logger.info(LOG_EXECUTING.format("Executing command: %s"), command)
            result = subprocess.run(
                command.get_chain_command(),
                env=environment_variables,
                shell=True,
                check=True,
            )
            if result.returncode != 0:
                logger.error(
                    "Command '%s' exited with non-zero return code: %s",
                    command,
                    result.returncode,
                )
            else:
                logger.debug(
                    "Command '%s' executed successfully with return code: %s",
                    command,
                    result.returncode,
                )
            return result.returncode == 0
        except Exception as e:
            logger.error("Error while running application: %s", e)
            raise RuntimeError(
                f"Error executing command: '{exe_command}' with compatibility tool."
            ) from e

    @staticmethod
    def run_chain_command(
        exe_command: list[str],
        logger: logging.Logger,
        *,
        environment_variables: dict[str, str] | None = None,
        cwd: str | None = None,
        dry_run: bool = False,
        detached: bool = False,
    ) -> subprocess.Popen[Any] | None:
        """
        Executes a given command using subprocess.Popen.

        Args:
            - exe_command (str): The command to execute,
            - logger (logging.Logger): The logger instance for logging execution
              details.
            - environment_variables (dict | None, optional): A dictionary of
              environment variables to override for the command. Defaults to None.
            - cwd (str | None, optional): The working directory to set for the
              command execution. Defaults to None.

        Returns:
            subprocess.Popen | None: The subprocess.Popen object for the
            executed command, or None if the execution fails.
        """
        try:
            if dry_run:
                logger.info(
                    LOG_DRY_RUN.format("Would execute command: %s"), exe_command
                )
                return None

            logger.info(
                LOG_EXECUTING.format("Executing command: %s"),
                exe_command,
            )
            # Ensure the working directory is an absolute path without symlinks
            # to avoid issues with subprocess and relative paths
            cwd = os.path.realpath(cwd or os.getcwd())
            if detached:
                # On Windows, use creationflags to detach the process
                return subprocess.Popen(
                    exe_command,
                    env=environment_variables,
                    cwd=cwd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                )
            return subprocess.Popen(
                exe_command,
                env=environment_variables,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
            )
        except Exception as e:
            logger.error("Error while running application: %s", e)
            raise RuntimeError(
                f"Error executing command: '{exe_command}' with execution pipeline."
            ) from e

    @staticmethod
    def run_in_external_terminal(
        terminal_command_template: list[str] | None,
        exe_command: str | Command,
        logger: logging.Logger,
        *,
        environment_variables: dict[str, str] | None = None,
        cwd: str | None = None,
        dry_run: bool = False,
    ):
        """
        Executes a given command in an external terminal.

        This function formats the terminal command template with the specific command,
        prepares the environment, and executes the command in a new terminal window or tab.
        If dry_run is enabled, it logs the command that would be executed without performing
        the actual execution.

        Args:
            terminal_command_template (list[str] | None): The template for the terminal
                command. Each element represents a part of the command, and parts that
                contain `{command}` will be replaced by the actual command.
            exe_command (str | ExecutableCommand): The command to execute, either as a
                string or an ExecutableCommand object.
            logger (logging.Logger): Logger instance for logging execution details and
                errors.
            environment_variables (dict[str, str] | None, optional): Custom environment
                variables to use during the execution. Defaults to None.
            cwd (str | None, optional): The working directory to set for the command
                execution. Defaults to None.
            dry_run (bool, optional): If True, the command is logged but not executed.
                Defaults to False.

        Raises:
            RuntimeError: If no terminal command template is provided, or if an error
            occurs while running the command in the terminal.
        """
        if terminal_command_template is None:
            logger.error("No terminal command template provided.")
            raise RuntimeError("No terminal command template provided.")

        try:
            actual_command = (
                exe_command
                if isinstance(exe_command, str)
                else exe_command.get_full_command()
            )
            if dry_run:
                logger.info(
                    LOG_DRY_RUN.format("Would execute command in terminal: %s"),
                    actual_command,
                )
                return None

            terminal_command = [
                part.format(command=actual_command)
                for part in terminal_command_template
            ]
            logger.info(
                LOG_EXECUTING.format("Executing command in terminal: %s"),
                " ".join(terminal_command),
            )
            return subprocess.Popen(
                terminal_command,
                env=environment_variables,
                cwd=cwd,
            )
        except Exception as e:
            logger.error("Error while running application in terminal: %s", e)
            raise RuntimeError(
                f"Error executing command: '{exe_command}' in terminal."
            ) from e

    @classmethod
    def run_with_pipeline(
        cls,
        exe_command: Command,
        runtime_configuration: RuntimeConfiguration,
        logger: logging.Logger,
        wrapper: CommandWrapper | None = None,
        detached: bool = False,
        custom_environment_variables: dict[str, str | None] | None = None,
    ) -> subprocess.Popen[Any] | None:
        """
        Runs a command within an execution pipeline, allowing for environment 
        variable modifications, optional detachment, and command wrapping.

        This method handles environmental customization, command construction, 
        and subprocess execution, seamlessly integrating optional wrappers and 
        detached operations. It honors runtime configuration settings such as 
        dry-run and ensures proper handling of the command execution.

        Args:
            exe_command (Command): The command to be executed within the pipeline.
            runtime_configuration (RuntimeConfiguration): Configuration details
                for runtime execution, including environment variables and 
                execution behavior.
            logger (logging.Logger): Logger for tracking execution details and outputs.
            wrapper (CommandWrapper | None, optional): Optional wrapper to modify
                the command before execution. Defaults to None.
            detached (bool, optional): Flag indicating if the execution should be detached.
                Defaults to False.
            custom_environment_variables (dict[str, str | None] | None, optional): 
                Additional environment variable settings. Variables mapped to 
                None are removed from the environment. Defaults to None.

        Returns:
            subprocess.Popen[Any] | None: Subprocess instance for the executed command
            or None if the execution is skipped or fails.
        """

        environment_variables = os.environ.copy()
        environment_variables.update(runtime_configuration.environment_variables or {})
        if custom_environment_variables:
            for key, value in custom_environment_variables.items():
                if value is None:
                    logger.debug(
                        "Removing environment variable '%s' as its custom value is set to None",
                        key,
                    )
                    environment_variables.pop(key, None)
                else:
                    logger.debug(
                        "Setting environment variable '%s' to custom value: %s",
                        key,
                        value,
                    )
                    environment_variables[key] = value

        command = cls.assemble_command_str(
            exe_command,
            runtime_configuration,
            logger,
            override_log_to_file=False,
        )
        cwd = (
            exe_command.cwd
            or (
                runtime_configuration.game_executable_command
                and runtime_configuration.game_executable_command.cwd
            )
            or "."
        )
        if wrapper:
            command = wrapper.wrap(
                command,
                runtime_configuration,
                command_category=exe_command.category,
                logger=logger,
            )
        os.makedirs(cwd, exist_ok=True)
        return cls.run_chain_command(
            command.get_chain_command(),
            logger,
            environment_variables=environment_variables,
            cwd=cwd,
            dry_run=runtime_configuration.dry_run,
            detached=detached,
        )
