import logging
import subprocess
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
        f"{runtime_configuration.steam_wrapper} "
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
        raise RuntimeError(f"Error executing {category} command: '{exe_command}' with compatibility tool.") from e


def run_game_and_forks_with_compatibility_tool(
    runtime_configuration: RuntimeConfiguration,
    logger: logging.Logger,
):
    for command in runtime_configuration.fork_commands or []:
        if (
            command.category == COMMAND_TRAINER
            and not runtime_configuration.execute_trainers
        ):
            continue  # Skip trainer commands if trainers are disabled

        full_command = f"{command.command} {command.args or ''}"
        run_with_compatibility_tool(
            full_command,
            runtime_configuration,
            logger,
            category=command.category or "uncategorized",
        )

    # Execute main game command
    run_with_compatibility_tool(
        runtime_configuration.steam_game_exe or "",
        runtime_configuration,
        logger,
    )
