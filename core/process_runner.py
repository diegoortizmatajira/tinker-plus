import logging
import subprocess
import time
from typing import Optional
from core.defaults import (
    GENERAL_TOOLS_LOG_FILE,
)
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
        logger.info("Executing command in Wine prefix: %s", command)
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
) -> Optional[subprocess.Popen]:
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
        return None
    try:
        logger.info("Executing %s command: %s", category, command)
        return subprocess.Popen(
            command,
            shell=True,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
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

        logger.info(
            "Running %s command: '%s'",
            command.category or "fork",
            command.get_full_command(),
        )
        run_with_compatibility_tool(
            command.get_full_command(),
            runtime_configuration,
            logger,
            category=command.category or "fork",
            is_fork=True,
        )
        time.sleep(2)  # Small delay to avoid

    if not runtime_configuration.steam_game_exe:
        raise RuntimeError("No game executable specified to run.")

    game_command = ExecutableCommand(runtime_configuration.steam_game_exe, "")
    logger.info(
        "Running game command: '%s'.",
        game_command.get_full_command(),
    )
    run_with_compatibility_tool(
        game_command.get_full_command(),
        runtime_configuration,
        logger,
    )
