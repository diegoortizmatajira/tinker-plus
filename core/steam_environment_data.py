from dataclasses import dataclass
import logging
import os
import re

from core.defaults import GAME_ENVIRONMENT_FILE_TEMPLATE
from core.file_operations import dump_as_json


@dataclass
class SteamEnvironmentData:
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

    def has_valid_data(self) -> bool:
        return self.steam_app_id is not None or self.steam_game_id is not None

    def parse_steam_command(
        self,
        full_command: str,
    ) -> None:
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

        def evaluate_match(input_str: str, pattern: str, group: str) -> str | None:
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
        exe_regexp = r"(^|\s)(?P<gameexe>(?:(?:\/[\w\.][\w\s\.\-\',]+\w)+\.exe))\s?(?P<gameargs>.*)$"

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
        self.parse_steam_command(full_command)
        self.parse_environment_variables(logger)

    def save(self, dry_run: bool, logger: logging.Logger) -> None:
        dump_as_json(
            self.__dict__,
            GAME_ENVIRONMENT_FILE_TEMPLATE.format(self.steam_game_id),
            dry_run,
            logger,
        )
