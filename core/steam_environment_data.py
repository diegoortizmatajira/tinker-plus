"""
Module for handling Steam environment data parsing and storage.
"""

from dataclasses import dataclass
import logging
import os
import re

from core.defaults import GAME_ENVIRONMENT_FILE_TEMPLATE
from core.file_operations import dump_as_json


@dataclass
class SteamEnvironmentData:
    """
    Data class to hold Steam environment data and parse relevant information
    """

    steam_app_id: str | None = None
    steam_game_id: str | None = None
    steam_compat_client_install_path: str | None = None
    steam_compat_install_path: str | None = None
    steam_fossilize_dump_path: str | None = None
    steam_runtime: str | None = None
    steam_client_config_file: str | None = None
    steam_compat_shader_path: str | None = None
    ld_preload: str | None = None
    steamscript_version: str | None = None
    steam_compat_media_path: str | None = None
    steam_compat_app_id: str | None = None
    steam_compat_data_path: str | None = None
    steam_compat_transcoded_media_path: str | None = None
    steam_base_folder: str | None = None
    cmd_steam_wrapper: str | None = None
    cmd_steam_reaper: str | None = None
    cmd_steam_sniper: str | None = None
    cmd_steam_compatibility_command: str | None = None
    cmd_steam_compatibility_tool: str | None = None
    cmd_steam_compatibility_tools_path: str | None = None
    cmd_steam_game_exe: str | None = None
    cmd_steam_game_args: str | None = None

    @staticmethod
    def empty() -> "SteamEnvironmentData":
        """
        Creates and returns an instance of SteamEnvironmentData with all fields set to None.

        Returns:
            SteamEnvironmentData: An instance with all attributes initialized to None.
        """
        return SteamEnvironmentData()

    def has_valid_data(self) -> bool:
        """
        Checks if the Steam environment data contains valid identifiers.
        """
        return self.steam_app_id is not None or self.steam_game_id is not None

    def parse_steam_command(self, full_command: str, logger: logging.Logger) -> None:
        """
        Parses the game command line and extracts runtime configuration components.

        This method analyzes the original command line for specific runtime components
        such as the Steam Launch Wrapper, Reaper command, Sniper command, Compatibility
        Tool, and Game Executable. If the parsed components match the expected pattern,
        they are logged and assigned to the runtime configuration attributes. If the
        parsing fails, a warning is logged.

        Logs:
            - Logs the identified components or warnings if the pattern does not match.
        """

        def evaluate_match(input_str: str, pattern: str, group: str) -> str | None:
            try:
                match = re.search(pattern, input_str)
                if match:
                    return match.group(group)
                return None
            except Exception as e:
                logger.warning("Regex error while parsing command: %s", e)
                return None

        wrapper_regexp = r"(?P<stlwrapper>\/\S+\/steam-launch-wrapper)"
        reaper_regexp = r"(?P<reaper>\/\S+\/reaper)"
        sniper_regexp = r"(?P<sniper>\/\S+\/SteamLinuxRuntime_sniper\/\S+\s+--\w+=\w+)"
        compatibility_regexp = (
            r"(?P<compatibility>"
            r"(?P<compatibility_dir>(?:\/[\w\.][\.\w\s\-']+\w)+)\/"
            r"(?P<compatibility_tool>[\w\.\-\s]+)\/\S+\swaitforexitandrun)\s+"
        )
        exe_regexp = r"(^|\s)(?P<gameexe>(?:(?:\/[\w\.][\w\s\.\-\',]*?\w)+\.exe))\s?(?P<gameargs>.*)$"

        self.cmd_steam_wrapper = evaluate_match(
            full_command, wrapper_regexp, "stlwrapper"
        )
        self.cmd_steam_reaper = evaluate_match(full_command, reaper_regexp, "reaper")
        self.cmd_steam_sniper = evaluate_match(full_command, sniper_regexp, "sniper")
        compatibility_match = re.search(compatibility_regexp, full_command)
        if compatibility_match:
            self.cmd_steam_compatibility_command = compatibility_match.group(
                "compatibility"
            )
            self.cmd_steam_compatibility_tool = compatibility_match.group(
                "compatibility_tool"
            )
            self.cmd_steam_compatibility_tools_path = compatibility_match.group(
                "compatibility_dir"
            )
        exe_match = re.search(exe_regexp, full_command)
        if not exe_match:
            logger.error("Failed to parse game executable from command line.")
            raise RuntimeError(
                "Game executable pattern did not match the command line."
            )
        self.cmd_steam_game_exe = exe_match.group("gameexe")
        self.cmd_steam_game_args = exe_match.group("gameargs")

    def parse_environment_variables(self, logger: logging.Logger):
        """
        Parses and assigns relevant steam environment variables to the given data object.

        This function reads specific environment variables, processes their values
        (removing surrounding quotes if present), and assigns them to corresponding
        attributes of the SteamEnvironmentData object.

        Args:
            data (SteamEnvironmentData): The object where the parsed
            environment variables will be stored.
        """

        def from_env(environment_variable: str) -> str | None:
            value = os.getenv(environment_variable)
            if value and (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
            ):
                value = value[1:-1]
            logger.info(
                "From environment variable:   %s=%s", environment_variable, value
            )
            return value

        self.steam_app_id = from_env("SteamAppId")
        self.steam_game_id = from_env("SteamGameId")
        self.steam_base_folder = from_env("STEAM_BASE_FOLDER")
        self.steam_compat_install_path = from_env("STEAM_COMPAT_INSTALL_PATH")
        self.steam_compat_data_path = from_env("STEAM_COMPAT_DATA_PATH")

    def parse(self, full_command: str, logger: logging.Logger) -> None:
        """
        Parses the full Steam command and environment variables to populate the relevant fields.

        This method combines the parsing of the command line and environment variables to
        populate the SteamEnvironmentData object with the corresponding runtime configuration
        and environment data.

        Args:
            full_command (str): The full command string containing game runtime
            and executable details.
            logger (logging.Logger): The logger instance used for logging parsing actions.
        """
        self.parse_steam_command(full_command, logger)
        self.parse_environment_variables(logger)

    def save(self, dry_run: bool, logger: logging.Logger) -> None:
        """
        Saves the current Steam environment data to a JSON file.

        This method serializes the SteamEnvironmentData object into a JSON
        representation and writes it to the location specified by the
        GAME_ENVIRONMENT_FILE_TEMPLATE. If dry_run is True, the data is
        logged instead of being written to a file.

        Args:
            dry_run (bool): If True, the JSON data will be logged instead of saved.
            logger (logging.Logger): The logger instance used for logging actions.
        """
        dump_as_json(
            self.__dict__,
            GAME_ENVIRONMENT_FILE_TEMPLATE.format(self.steam_game_id),
            dry_run,
            logger,
        )
