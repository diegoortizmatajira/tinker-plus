import logging
import subprocess
from typing import Optional
from core.defaults import (
    GENERAL_TOOLS_LOG_FILE,
)
from core.runtime_configuration import COMMAND_TRAINER, RuntimeConfiguration


def run_in_wine_prefix(
    exe_command: str,
    runtime_configuration: RuntimeConfiguration,
    logger: logging.Logger,
    output_log_file: Optional[str] = None,
):
    """
    Executes a given command within a specified Wine prefix using subprocess.

    Args:
        command (str): The command to execute.
    """
    wine_prefix = runtime_configuration.prefix_path
    if not wine_prefix:
        raise RuntimeError("WINEPREFIX environment variable is not set.")

    command = (
        f'WINEPREFIX="{wine_prefix}" {exe_command} >> '
        f"{output_log_file or GENERAL_TOOLS_LOG_FILE} 2>&1"
    )
    if runtime_configuration.dry_run:
        logger.info("[DRY RUN] Would execute command in Wine prefix: %s", command)
        return
    try:
        subprocess.run(command, shell=True, check=True)
    except Exception as e:
        logger.error("Error while running command in Wine prefix: %s", e)
        raise RuntimeError(
            f"Error executing command in Wine prefix: '{exe_command}'"
        ) from e


def run_with_compatibility_tool(
    exe_command: str,
    runtime_configuration: RuntimeConfiguration,
    logger: logging.Logger,
    *,
    category: str = "main game",
    is_fork: bool = False,
):
    """
    Executes a given command using subprocess.

    Args:
        command (str): The command to execute.
    """

    environment_variables = ""
    if runtime_configuration.environment_variables:
        environment_variables = " ".join(
            [
                f"{key}={value if ' ' not in value else f'''{value}'''}"
                for key, value in (runtime_configuration.environment_variables).items()
            ]
        ).strip()

    command = exe_command
    # Takes the pipeline wrappers in reverse order
    for wrapper in reversed(runtime_configuration.pipeline_wrappers or []):
        command = wrapper.wrap(
            command, runtime_configuration, is_fork=is_fork, logger=logger
        )

    command = f"{environment_variables} {command}"
    if runtime_configuration.dry_run:
        logger.info("[DRY RUN] Would execute %s command: %s", category, command)
        return
    try:
        logger.info("Executing %s command: %s", category, command)
        bash_wrapper = f"bash {command}"
        # subprocess.run(bash_wrapper, shell=True, check=True)
        with subprocess.Popen(bash_wrapper) as process:
            process.wait()
    except Exception as e:
        logger.error("Error while running application: %s", e)
        raise RuntimeError(
            f"Error executing {category} command: '{exe_command}' with compatibility tool."
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

    for command in runtime_configuration.fork_commands or []:
        if (
            command.category == COMMAND_TRAINER
            and not runtime_configuration.execute_trainers
        ):
            continue  # Skip trainer commands if trainers are disabled

        full_command = f'"{command.command}" {command.args or ""}'.strip()
        logger.info(
            "Running %s command: '%s'",
            command.category or "fork",
            full_command,
        )
        run_with_compatibility_tool(
            full_command,
            runtime_configuration,
            logger,
            category=command.category or "fork",
            is_fork=True,
        )

    if not runtime_configuration.steam_game_exe:
        raise RuntimeError("No game executable specified to run.")

    logger.info(
        "Running game command: '%s'.",
        runtime_configuration.steam_game_exe,
    )
    run_with_compatibility_tool(
        runtime_configuration.steam_game_exe,
        runtime_configuration,
        logger,
    )
