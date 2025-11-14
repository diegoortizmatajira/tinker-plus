import logging
import os
import subprocess
from core.defaults import GAME_BAT_LAUNCHER_DIR, GAME_BAT_LAUNCHER_FILE_TEMPLATE
from core.runtime_configuration import COMMAND_TRAINER, RuntimeConfiguration


def run_with_compatibility_tool(
    exe_command: str,
    runtime_configuration: RuntimeConfiguration,
    logger: logging.Logger,
    *,
    category: str = "main game",
):
    """
    Executes a given command using subprocess.

    Args:
        command (str): The command to execute.
    """

    compatibility_tool = (
        f"{runtime_configuration.steam_compatibility_tools_path}/"
        f"{runtime_configuration.steam_compatibility_tool}/proton waitforexitandrun"
    )
    command = (
        #        f"{runtime_configuration.steam_wrapper} "
        f"{runtime_configuration.steam_reaper} "
        f"SteamLaunch AppId={runtime_configuration.steam_app_id} -- "
        f"{runtime_configuration.steam_sniper} -- "
        f"{compatibility_tool} {exe_command}"
    )
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
    bat_content = ""

    for command in runtime_configuration.fork_commands or []:
        if (
            command.category == COMMAND_TRAINER
            and not runtime_configuration.execute_trainers
        ):
            continue  # Skip trainer commands if trainers are disabled

        full_command = f'"{command.command}" {command.args or ""}'.strip()
        logger.info(
            "Including %s command: '%s' in launcher script.",
            command.category,
            full_command,
        )
        bat_content += f'start "" {full_command}\n'

    logger.info(
        "Including game command: '%s' in launcher script.",
        runtime_configuration.steam_game_exe,
    )
    bat_content += f'start "" "{runtime_configuration.steam_game_exe}"\n'
    # Write the batch file to a temporary location (create directory if it doesn't exist)
    os.makedirs(GAME_BAT_LAUNCHER_DIR, exist_ok=True)
    bat_file_path = str.format(
        GAME_BAT_LAUNCHER_FILE_TEMPLATE, runtime_configuration.steam_game_id
    )
    #
    with open(bat_file_path, "w", encoding="utf-8") as bat_file:
        bat_file.write(bat_content)
    # Execute the batch file using the compatibility tool
    run_with_compatibility_tool(
        bat_file_path,
        runtime_configuration,
        logger,
    )
