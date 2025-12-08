"""Module to centralize Steam-related constants and utilities."""

import logging
import os
from pathlib import Path
import re
from typing import Optional
from core.defaults import DEFAULT_STEAM_APP_CACHE_FOLDER, STEAM_MANIFESTS_TEMPLATE
from core.game_info import GameInfo
from core.runtime_configuration import RuntimeConfiguration


def get_steam_header_image_path(
    runtime_configuration: RuntimeConfiguration,
) -> Optional[str]:
    """
    Constructs the file path for the Steam header image of a given game.

    Args:
        game_id (str): The unique identifier for the Steam game.
    Returns:
        str: The file path to the Steam header image.
    """

    cache_dir = Path(
        DEFAULT_STEAM_APP_CACHE_FOLDER.format(
            runtime_configuration.steam_base_folder,
            runtime_configuration.steam_game_id,
        )
    )
    if not cache_dir.exists():
        return None
    candidates = cache_dir.glob("**/*header.jpg")
    for candidate in candidates:
        return candidate.as_posix()
    return None


def get_wine(
    runtime_configuration: RuntimeConfiguration, logger: logging.Logger
) -> str:
    """
    Retrieves the Wine executable path from the runtime configuration.

    Returns:
        str: The Wine executable path.
    """

    compat_tool_path = os.path.join(
        runtime_configuration.steam_compatibility_tools_path or "missing",
        runtime_configuration.steam_compatibility_tool or "missing",
    )
    proton_wine = os.path.join(compat_tool_path, "dist/bin/wine")
    ge_proton_wine = os.path.join(compat_tool_path, "files/bin/wine")
    logger.debug("Checking for Proton Wine at: %s", proton_wine)
    if os.path.isfile(proton_wine):
        logger.info("Found Proton Wine at: %s", proton_wine)
        return proton_wine
    logger.debug("Checking for GE-Proton Wine at: %s", ge_proton_wine)
    if os.path.isfile(ge_proton_wine):
        logger.info("Found GE-Proton Wine at: %s", ge_proton_wine)
        return ge_proton_wine
    logger.warning(
        "Could not find a valid Wine executable in the compatibility tool path."
    )
    return ""


def get_game_info(
    runtime_configuration: RuntimeConfiguration, logger: logging.Logger
) -> GameInfo:
    """
    Determines the name of the game based on the Steam manifest file or the executable name.

    Args:
        runtime_configuration (RuntimeConfiguration): The runtime configuration providing the
        Steam base folder and game ID.

    Returns:
        str: The name of the game as extracted from the Steam manifest file,
        or the executable name as a fallback.
    """
    game_id = (
        runtime_configuration.steam_game_id
        or runtime_configuration.steam_app_id
        or "unknown"
    )
    logger.debug("Getting game info for Game ID: %s", game_id)
    game_info = GameInfo.from_cache(game_id, logger)
    if game_info:
        logger.debug("Found game info in cache: %s", game_info)
        return game_info

    manifest_path = STEAM_MANIFESTS_TEMPLATE.format(
        runtime_configuration.steam_base_folder,
        runtime_configuration.steam_game_id,
    )
    game_info = GameInfo(
        game_id=game_id,
        name=Path(runtime_configuration.steam_game_exe or "unknown").stem,
    )
    logger.debug("Looking for Steam manifest at: %s", manifest_path)
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as manifest_file:
                for line in manifest_file:
                    if '"name"' in line:
                        # Extract the game name from the line
                        name = line.split('"')[3]
                        game_info.name = name
        except Exception as e:
            logger.warning(
                "An error occurred while reading the Steam manifest file: %s", e
            )
    else:
        logger.warning("Steam manifest file does not exist at: %s", manifest_path)
    game_info.put_in_cache(logger)
    # Fallback to using the executable name if manifest reading fails
    return game_info


def parse_steam_command(runtime_configuration: RuntimeConfiguration):
    """
    Parses the game command line and extracts runtime configuration components.

    This method analyzes the original command line for specific runtime components
    such as the Steam Launch Wrapper, Reaper command, Sniper command, Compatibility
    Tool, and Game Executable. If the parsed components match the expected pattern,
    they are logged and assigned to the runtime configuration attributes. If the
    parsing fails, a warning is logged.

    Updates:
        - runtime_configuration.steam_wrapper: The Steam Launch Wrapper command.
        - runtime_configuration.steam_reaper: The Reaper command.
        - runtime_configuration.steam_sniper: The Sniper command.
        - runtime_configuration.steam_compatibility_tool: The Compatibility Tool command.
        - runtime_configuration.steam_game_exe: The Game Executable command.

    Logs:
        - Logs the identified components or warnings if the pattern does not match.
    """

    def evaluate_match(input_str: str, pattern: str, group) -> Optional[str]:
        match = re.search(pattern, input_str)
        if match:
            return match.group(group)
        return None

    wrapper_regexp = r"(?P<stlwrapper>\/\S+\/steam-launch-wrapper)"
    reaper_regexp = r"(?P<reaper>\/\S+\/reaper)"
    sniper_regexp = r"(?P<sniper>\/\S+\/SteamLinuxRuntime_sniper\/\S+\s+--\w+=\w+)"
    compatibility_regexp = (
        r"(?P<compatibility>"
        r"(?P<compatibility_dir>(?:\/[\w\.][\.\w\s\-']+\w)+)\/"
        r"(?P<compatibility_tool>[\w\.\-\s]+)\/\S+\swaitforexitandrun)\s+"
    )
    exe_regexp = (
        r"(^|\s)(?P<gameexe>(?:(?:\/[\w\.][\w\s\.\-\',]+\w)+\.exe))\s?(?P<gameargs>.*)$"
    )

    full_command = " ".join(runtime_configuration.original_command)
    runtime_configuration.steam_wrapper = evaluate_match(
        full_command, wrapper_regexp, "stlwrapper"
    )
    runtime_configuration.steam_reaper = evaluate_match(
        full_command, reaper_regexp, "reaper"
    )
    runtime_configuration.steam_sniper = evaluate_match(
        full_command, sniper_regexp, "sniper"
    )
    compatibility_match = re.search(compatibility_regexp, full_command)
    if compatibility_match:
        runtime_configuration.steam_compatibility_command = compatibility_match.group(
            "compatibility"
        )
        runtime_configuration.steam_compatibility_tool = compatibility_match.group(
            "compatibility_tool"
        )
        runtime_configuration.steam_compatibility_tools_path = (
            compatibility_match.group("compatibility_dir")
        )
    exe_match = re.search(exe_regexp, full_command)
    if not exe_match:
        raise RuntimeError("Game executable pattern did not match the command line.")
    runtime_configuration.steam_game_exe = exe_match.group("gameexe")
    runtime_configuration.steam_game_args = exe_match.group("gameargs")
