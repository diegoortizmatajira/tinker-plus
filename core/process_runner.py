"""Module for running processes with compatibility tools and handling execution pipelines."""

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, overload

from core.defaults import (
    GAME_SCRIPT_TEMPLATE,
    LOG_DRY_RUN,
    LOG_EXECUTING,
)
from core.log_storage import LogFactory
from core.runtime_configuration import (
    COMMAND_TRAINER,
    ExecutableCommand,
    RuntimeConfiguration,
)


@overload
def run_in_wine_prefix(
    exe_command: ExecutableCommand,
    runtime_configuration: RuntimeConfiguration,
    logger: logging.Logger,
) -> bool:
    """
    Executes the given command in a Wine prefix environment.

    This function sets the necessary environment variables for Wine,
    constructs the command with optional logging or dry-run behaviors,
    and executes it using the subprocess module. The execution can also
    capture output if explicitly enabled.

    Args:
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
def run_in_wine_prefix(
    exe_command: ExecutableCommand,
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


def run_in_wine_prefix(
    exe_command: ExecutableCommand,
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


def __assemble_command_str(
    exe_command: str | ExecutableCommand,
    runtime_configuration: RuntimeConfiguration,
    is_global: bool = True,
    is_fork: bool = False,
    override_log_to_file: bool | None = None,
) -> str:
    actual_command = (
        exe_command if isinstance(exe_command, str) else exe_command.get_full_command()
    )
    # Takes the pipeline wrappers in reverse order
    for wrapper in reversed(runtime_configuration.pipeline_wrappers or []):
        actual_command = wrapper.wrap(
            actual_command,
            runtime_configuration,
            is_global=is_global,
            is_fork=is_fork,
            logger=logging.getLogger(),
        )
    # Only log to file if the command is an ExecutableCommand and logging is enabled
    if (
        runtime_configuration.log_executable_commands
        and not isinstance(exe_command, str)
        and (override_log_to_file is not False)
    ):
        exe_path = Path(exe_command.command)
        log_file = LogFactory.singleton().get_log_filename(f"{exe_path.stem}.log")
        actual_command = f"{actual_command} >> {log_file} 2>&1"
    return actual_command


def run_command_with_compatibility_tool(
    exe_command: ExecutableCommand,
    runtime_configuration: RuntimeConfiguration,
    logger: logging.Logger,
) -> bool:
    """
    Executes a given command using a compatibility tool defined in the runtime configuration.

    Args:
        command (str): The command to execute.
    """

    environment_variables = os.environ.copy()
    environment_variables.update(runtime_configuration.environment_variables or {})
    command = __assemble_command_str(
        exe_command, runtime_configuration, is_global=False, is_fork=True
    )
    if runtime_configuration.dry_run:
        logger.info(LOG_DRY_RUN.format("Would execute command: %s"), command)
        return True
    try:
        logger.info(LOG_EXECUTING.format("Executing command: %s"), command)
        result = subprocess.run(
            command, env=environment_variables, shell=True, check=True
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


def run_command(
    exe_command: str | ExecutableCommand,
    logger: logging.Logger,
    *,
    environment_variables: dict[str, str] | None = None,
    cwd: str | None = None,
    dry_run: bool = False,
) -> subprocess.Popen[Any] | None:
    """
    Executes a given command using subprocess.Popen.

    Args:
        - exe_command (Union[str, ExecutableCommand]): The command to execute,
          either as a string or an ExecutableCommand object.
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
        actual_command = (
            exe_command
            if isinstance(exe_command, str)
            else exe_command.get_full_command()
        )

        if dry_run:
            logger.info(LOG_DRY_RUN.format("Would execute command: %s"), actual_command)
            return None

        logger.info(
            LOG_EXECUTING.format("Executing command: %s"),
            actual_command,
        )
        return subprocess.Popen(
            actual_command,
            env=environment_variables,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
        )
    except Exception as e:
        logger.error("Error while running application: %s", e)
        raise RuntimeError(
            f"Error executing command: '{exe_command}' with execution pipeline."
        ) from e


def run_in_external_terminal(
    terminal_command_template: list[str] | None,
    exe_command: str | ExecutableCommand,
    logger: logging.Logger,
    *,
    environment_variables: dict[str, str] | None = None,
    cwd: str | None = None,
    dry_run: bool = False,
):
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
            part.format(command=actual_command) for part in terminal_command_template
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


def run_with_pipeline(
    exe_command: str | ExecutableCommand,
    runtime_configuration: RuntimeConfiguration,
    logger: logging.Logger,
) -> subprocess.Popen[Any] | None:
    """
    Executes a given command using subprocess.

    Args:
        command (str): The command to execute.
    """

    environment_variables = os.environ.copy()
    environment_variables.update(runtime_configuration.environment_variables or {})
    command = __assemble_command_str(
        exe_command, runtime_configuration, is_global=True, override_log_to_file=False
    )
    cwd = (
        runtime_configuration.game_executable_command
        and runtime_configuration.game_executable_command.cwd
        or "."
    )
    os.makedirs(cwd, exist_ok=True)
    return run_command(
        command,
        logger,
        environment_variables=environment_variables,
        cwd=cwd,
        dry_run=runtime_configuration.dry_run,
    )


def run_game_and_forks_with_compatibility_tool(
    runtime_configuration: RuntimeConfiguration,
    logger: logging.Logger,
):
    """
    Prepares and executes a game and its associated fork commands using a compatibility tool.

    This function generates a batch script (.bat) that includes the commands to be run,
    such as forked processes and the main game executable. The generated script is then
    executed using the defined compatibility tool.

    Args:
        runtime_configuration (RuntimeConfiguration): The configuration object containing
            details about the runtime environment, such as fork commands, game executable,
            and compatibility tools.
        logger (logging.Logger): The logger instance for logging progress and errors.
    """
    forks_to_include = [
        fork
        for fork in runtime_configuration.fork_commands or []
        if (
            fork.category == COMMAND_TRAINER
            and not runtime_configuration.execute_trainers
        )
        is False
    ]

    added_forks = len(forks_to_include)

    if (
        not runtime_configuration.execute_forks_only
        and not runtime_configuration.game_executable_command
    ):
        logger.error("No game executable specified to run.")
        raise RuntimeError("No game executable specified to run.")

    if added_forks == 0 and runtime_configuration.execute_forks_only:
        logger.error("No fork commands were added, and 'forks only' mode is enabled.")
        raise RuntimeError("No fork commands to execute in 'forks only' mode.")

    if added_forks > 0:
        logger.info("Using launcher script to run forks and game executable.")

        launcher_script_content = "#!/bin/bash\n"
        launcher_command_lines: list[str] = []
        for command in forks_to_include:
            command_category = command.category or "fork"
            logger.info(
                "Including %s command in launcher script: '%s'",
                command_category,
                command.get_full_command(),
            )
            command_line = f"# {command_category} command\n"
            assembled_command_str = __assemble_command_str(
                command,
                runtime_configuration,
                is_global=False,
                is_fork=True,
            )
            command_line += f"{assembled_command_str}"
            launcher_command_lines.append(command_line)

        launcher_script_content += " & \n".join(launcher_command_lines)

        if (
            not runtime_configuration.execute_forks_only
            and runtime_configuration.game_executable_command
        ):
            launcher_script_content += " & \n"
            logger.info(
                "Including game command in launcher script: '%s'.",
                runtime_configuration.game_executable_command.get_full_command(),
            )
            launcher_script_content += "# main game command\n"

            assembled_command_str = __assemble_command_str(
                runtime_configuration.game_executable_command,
                runtime_configuration,
                is_global=False,
            )
            launcher_script_content += f"{assembled_command_str}\n"
        script_filename = GAME_SCRIPT_TEMPLATE.format(
            runtime_configuration.get_game_identifier()
        )
        # Write the launcher script to a file
        with open(script_filename, "w", encoding="utf-8") as script_file:
            _ = script_file.write(launcher_script_content)
        os.chmod(script_filename, 0o755)  # Make the script executable
    else:
        if not runtime_configuration.game_executable_command:
            logger.error("No game executable specified to run.")
            raise RuntimeError("No game executable specified to run.")
        # No forks to include; run the game executable directly
        logger.info(
            "Including game command in launcher script: '%s'.",
            runtime_configuration.game_executable_command.get_full_command(),
        )
        script_filename = __assemble_command_str(
            runtime_configuration.game_executable_command,
            runtime_configuration,
            is_global=False,
        )

    game_process = run_with_pipeline(
        script_filename,
        runtime_configuration,
        logger,
    )
    if game_process:
        with game_process:
            logger.info("Launched game with PID: %s", game_process.pid)
            result = game_process.wait()
            logger.info("Game process exited with return code: %s", result)
