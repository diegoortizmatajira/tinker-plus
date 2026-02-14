"""Module to centralize Steam-related constants and utilities."""

import logging
import os
from pathlib import Path
from typing import final
from model import GameInfo, RuntimeConfiguration
from repositories import GameInfoRepository
from .steam_parser import SteamParser
from .defaults import DEFAULT_STEAM_APP_CACHE_FOLDER, STEAM_MANIFESTS_TEMPLATE


@final
class SteamUtil:
    """
    The SteamUtil class provides utility functions related to Steam, such as
    retrieving the Steam header image path, determining the Wine executable
    path, and extracting game information from the Steam manifest file. These
    utilities are designed to work with the runtime configuration and assist in
    managing Steam-related data for the Tinker Plus application.
    """

    @staticmethod
    def get_steam_header_image_path(
        runtime_configuration: RuntimeConfiguration,
    ) -> str | None:
        """
        Constructs the file path for the Steam header image of a given game.

        Args:
            game_id (str): The unique identifier for the Steam game.
        Returns:
            str: The file path to the Steam header image.
        """

        cache_dir = Path(
            DEFAULT_STEAM_APP_CACHE_FOLDER.format(
                runtime_configuration.steam_environment_data.steam_base_folder,
                runtime_configuration.get_game_identifier(),
            )
        )
        if not cache_dir.exists():
            return None
        candidates = cache_dir.glob("**/*header.jpg")
        for candidate in candidates:
            return candidate.as_posix()
        return None

    @staticmethod
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

    @staticmethod
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
        if not SteamParser.has_valid_data(runtime_configuration.steam_environment_data):
            return GameInfo.empty()

        game_id = runtime_configuration.get_game_identifier()
        logger.debug("Getting game info for Game ID: %s", game_id)
        game_info = GameInfoRepository.from_cache(game_id, logger)
        if game_info:
            logger.debug("Found game info in cache: %s", game_info)
            return game_info

        manifest_path = STEAM_MANIFESTS_TEMPLATE.format(
            runtime_configuration.steam_environment_data.steam_base_folder,
            runtime_configuration.get_game_identifier(),
        )
        game_info = GameInfo(
            game_id=game_id,
            name=Path(
                runtime_configuration.game_executable_command
                and runtime_configuration.game_executable_command.command
                or "unknown"
            ).stem,
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
        GameInfoRepository.put_in_cache(game_info, logger)
        # Fallback to using the executable name if manifest reading fails
        return game_info

    @staticmethod
    def get_anonymous_steam_overrides() -> dict[str, str | None]:
        """
        Generates a dictionary of Steam environment variable overrides,
        setting specific variables to `None` to ensure that they are removed
        from the environment for running trainers without Game ID.

        Returns:
            dict[str, str | None]: A dictionary where keys are the names of
            environment variables to be removed, and their values are set to
            `None`, indicating removal.
        """
        environment_vars_to_remove = [
            "SteamGameId",
            "SteamAppId",
            "SteamInput",
            "SteamControllerAppId",
            "STEAM_COMPAT_APP_ID",
            "SteamOverlayGameId",
            "SteamClientLaunch",
            "STEAM_COMPAT_PROTON",
            "LD_PRELOAD",
        ]
        # Setting the environment variables to None will remove them from the
        # environment of the trainer processes
        return {key: None for key in environment_vars_to_remove}
