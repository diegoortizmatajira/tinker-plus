"""Module for running processes with compatibility tools and handling execution pipelines."""

import logging
import os
import subprocess
from typing import Optional
from core.defaults import (
    GAME_SCRIPT_TEMPLATE,
    GENERAL_TOOLS_LOG_FILE,
)
from core.log_storage import LogFactory
from core.runtime_configuration import (
    COMMAND_TRAINER,
    ExecutableCommand,
    RuntimeConfiguration,
)


def run_in_wine_prefix(
    exe_command: str,
    runtime_configuration: RuntimeConfiguration,
    logger: logging.Logger,
    output_log_file: Optional[str] = None,
) -> bool:
    """
    Executes a given command within a specified Wine prefix using subprocess.

    Args:
        command (str): The command to execute.
    """
    wine_prefix = runtime_configuration.prefix_path
    if not wine_prefix:
        raise RuntimeError("WINEPREFIX environment variable is not set.")

    log_file = LogFactory.singleton().get_log_filename(
        output_log_file or GENERAL_TOOLS_LOG_FILE
    )
    environment_variables = os.environ.copy()
    environment_variables.update(runtime_configuration.environment_variables or {})
    environment_variables["WINEPREFIX"] = wine_prefix
    logger.info("Using  WINEPREFIX=%s", wine_prefix)
    if runtime_configuration.wine:
        environment_variables["WINE"] = runtime_configuration.wine
        logger.info("Using  WINE=%s", runtime_configuration.wine)

    command = f"{exe_command} >> {log_file} 2>&1"
    if runtime_configuration.dry_run:
        logger.info("[DRY RUN] Would execute command in Wine prefix: %s", command)
        return True
    try:
        logger.info("Executing command in Wine prefix: %s", command)
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
        logger.error("Error while running command in Wine prefix: %s", e)
        raise RuntimeError(
            f"Error executing command in Wine prefix: '{exe_command}'"
        ) from e


def __assemble_command_str(
    exe_command: str,
    runtime_configuration: RuntimeConfiguration,
    is_global: bool = True,
    is_fork: bool = False,
) -> str:
    command = exe_command
    # Takes the pipeline wrappers in reverse order
    for wrapper in reversed(runtime_configuration.pipeline_wrappers or []):
        command = wrapper.wrap(
            command,
            runtime_configuration,
            is_global=is_global,
            is_fork=is_fork,
            logger=logging.getLogger(),
        )
    return command


def run_with_pipeline(
    exe_command: str,
    runtime_configuration: RuntimeConfiguration,
    logger: logging.Logger,
) -> Optional[subprocess.Popen]:
    """
    Executes a given command using subprocess.

    Args:
        command (str): The command to execute.
    """

    environment_variables = os.environ.copy()
    environment_variables.update(runtime_configuration.environment_variables or {})
    command = __assemble_command_str(exe_command, runtime_configuration, is_global=True)
    if runtime_configuration.dry_run:
        logger.info("[DRY RUN] Would execute command: %s", command)
        return None
    try:
        logger.info("Executing command: %s", command)
        return subprocess.Popen(
            command,
            env=environment_variables,
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
    launcher_script_content = "#!/bin/bash\n"
    added_forks = 0
    if runtime_configuration.fork_commands:
        last_index = len(runtime_configuration.fork_commands) - 1
        for index, command in enumerate(runtime_configuration.fork_commands):
            if (
                command.category == COMMAND_TRAINER
                and not runtime_configuration.execute_trainers
            ):
                continue  # Skip trainer commands if trainers are disabled
            command_category = command.category or "fork"
            logger.info(
                "Including %s command in launcher script: '%s'",
                command_category,
                command.get_full_command(),
            )
            launcher_script_content += f"# {command_category} command\n"
            assembled_command_str = __assemble_command_str(
                command.get_full_command(),
                runtime_configuration,
                is_global=False,
                is_fork=True,
            )
            # Determine if we need to add '&' to run in background
            suffix = (
                "&"
                if (index < last_index) or not runtime_configuration.execute_forks_only
                else ""
            )
            launcher_script_content += f"{assembled_command_str} {suffix}\n"
            added_forks += 1
    if added_forks == 0 and runtime_configuration.execute_forks_only:
        logger.warning(
            "No fork commands were added, and 'forks only' mode is enabled. "
            "The launcher script will not execute any commands."
        )
        raise RuntimeError("No fork commands to execute in 'forks only' mode.")
    if not runtime_configuration.execute_forks_only:
        if not runtime_configuration.steam_game_exe:
            logger.error("No game executable specified to run.")
            raise RuntimeError("No game executable specified to run.")

        game_command = ExecutableCommand(
            runtime_configuration.steam_game_exe,
            runtime_configuration.steam_game_args,
        )
        logger.info(
            "Including game command in launcher script: '%s'.",
            game_command.get_full_command(),
        )
        launcher_script_content += "# main game command\n"

        assembled_command_str = __assemble_command_str(
            game_command.get_full_command(),
            runtime_configuration,
            is_global=False,
        )
        launcher_script_content += f"{assembled_command_str}\n"
    script_filename = GAME_SCRIPT_TEMPLATE.format(runtime_configuration.steam_game_id)
    # Write the launcher script to a file
    with open(script_filename, "w", encoding="utf-8") as script_file:
        script_file.write(launcher_script_content)
    os.chmod(script_filename, 0o755)  # Make the script executable
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
