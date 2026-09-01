"""Module to centralize Steam-related constants and utilities."""

import json
import logging
import os
import re
from typing import final

from file_system import FileSystem
from model import SteamEnvironmentData

from defaults import GAME_ENVIRONMENT_FILE_TEMPLATE

REGEX_WRAPPER = r"(?P<stlwrapper>\/\S+\/steam-launch-wrapper)"
REGEX_REAPER = r"(?P<reaper>\/\S+\/reaper)"
REGEX_SNIPER = r"(?P<sniper>\/\S+\/SteamLinuxRuntime_sniper\/\S+\s+--\w+=\w+)"
REGEX_COMPATIBILITY = (
    r"(?P<compatibility>"
    + r"(?P<compatibility_dir>(?:\/[\w\.][\.\w\s\-']+\w)+)\/"
    + r"(?P<compatibility_tool>[\w\.\-\s]+)\/\S+\swaitforexitandrun)\s+"
)
REGEXP_EXE = (
    r"(^|\s)(?P<gameexe>(?:(?:\/[\w\.][\w\s\.\-\',]*?\w)+\.exe))\s?(?P<gameargs>.*)$"
)

ENV_STEAM_APP_ID = "SteamAppId"
ENV_STEAM_GAME_ID = "SteamGameId"
ENV_STEAM_BASE_FOLDER = "STEAM_BASE_FOLDER"
ENV_STEAM_COMPAT_APP_ID = "STEAM_COMPAT_APP_ID"
ENV_STEAM_COMPAT_INSTALL_PATH = "STEAM_COMPAT_INSTALL_PATH"
ENV_STEAM_COMPAT_DATA_PATH = "STEAM_COMPAT_DATA_PATH"
ENV_STEAM_COMPAT_CLIENT_INSTALL_PATH = "STEAM_COMPAT_CLIENT_INSTALL_PATH"

ENV_LIST = [
    ENV_STEAM_APP_ID,
    ENV_STEAM_GAME_ID,
    ENV_STEAM_BASE_FOLDER,
    ENV_STEAM_COMPAT_APP_ID,
    ENV_STEAM_COMPAT_INSTALL_PATH,
    ENV_STEAM_COMPAT_DATA_PATH,
    ENV_STEAM_COMPAT_CLIENT_INSTALL_PATH,
    "STEAM_FOSSILIZE_DUMP_PATH",
    "STEAM_RUNTIME",
    "STEAM_CLIENT_CONFIG_FILE",
    "STEAM_ZENITY",
    "STEAMSCRIPT_VERSION",
    "STEAM_COMPAT_SHADER_PATH",
    "STEAM_COMPAT_MEDIA_PATH",
    "STEAM_COMPAT_TRANSCODED_MEDIA_PATH",
    "STEAM_COMPAT_MOUNTS",
    "SteamVirtualGamepadInfo_Proton",
    "STEAM_COMPAT_PROTON",
    "STEAM_COMPAT_TOOL_PATHS",
    "STEAM_FOSSILIZE_DUMP_PATH_READ_ONLY",
    "LD_LIBRARY_PATH",
    "AMD_VK_PIPELINE_CACHE_FILENAME",
    "AMD_VK_PIPELINE_CACHE_PATH",
    "SteamClientLaunch",
    "LD_PRELOAD",
    "MESA_GLSL_CACHE_MAX_SIZE",
    "FOSSILIZE_APPLICATION_INFO_FILTER_PATH",
    "ENABLE_VK_LAYER_VALVE_steam_fossilize_1",
    "SDL_GAMECONTROLLER_ALLOW_STEAM_VIRTUAL_GAMEPAD",
    "SRT_LAUNCHER_SERVICE_ALONGSIDE_STEAM",
    "DXVK_STATE_CACHE_PATH",
    "MESA_DISK_CACHE_READ_ONLY_FOZ_DBS",
    "STEAMSCRIPT",
    "STEAM_COMPAT_FLAGS",
    "SteamOverlayGameId",
    "__GL_SHADER_DISK_CACHE_APP_NAME",
    "SteamEnv",
    "GIO_LAUNCHED_DESKTOP_FILE_PID",
    "SDL_JOYSTICK_HIDAPI_STEAMXBOX",
    "GIO_LAUNCHED_DESKTOP_FILE",
    "STEAM_COMPAT_LIBRARY_PATHS",
    "SteamUser",
    "OLDPWD",
    "STEAM_RUNTIME_LIBRARY_PATH",
    "TEXTDOMAIN",
]


@final
class SteamParser:
    """Utility class for parsing Steam environment data and command lines."""

    @staticmethod
    def has_valid_data(data: SteamEnvironmentData) -> bool:
        """
        Checks if the Steam environment data contains valid identifiers.

        Args:
            data (SteamEnvironmentData): The Steam environment data to check.

        Returns:
            bool: True if either the Steam app ID or Steam game ID is set.
        """
        return data.steam_app_id is not None or data.steam_game_id is not None

    @staticmethod
    def parse_steam_command(
        full_command: str, data: SteamEnvironmentData, logger: logging.Logger
    ) -> None:
        """
        Parses the game command line and extracts runtime configuration components.

        This method analyzes the original command line for specific runtime components
        such as the Steam Launch Wrapper, Reaper command, Sniper command, Compatibility
        Tool, and Game Executable. If the parsed components match the expected pattern,
        they are logged and assigned to the runtime configuration attributes. If the
        parsing fails, a warning is logged.

        Args:
            full_command (str): The full original launch command line to parse.
            data (SteamEnvironmentData): The object to populate with the parsed values.
            logger (logging.Logger): Logger instance for logging parse results/warnings.

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

        data.cmd_steam_wrapper = evaluate_match(
            full_command, REGEX_WRAPPER, "stlwrapper"
        )
        data.cmd_steam_reaper = evaluate_match(full_command, REGEX_REAPER, "reaper")
        data.cmd_steam_sniper = evaluate_match(full_command, REGEX_SNIPER, "sniper")
        compatibility_match = re.search(REGEX_COMPATIBILITY, full_command)
        if compatibility_match:
            data.cmd_steam_compatibility_command = compatibility_match.group(
                "compatibility"
            )
            data.cmd_steam_compatibility_tool = compatibility_match.group(
                "compatibility_tool"
            )
            data.cmd_steam_compatibility_tools_path = compatibility_match.group(
                "compatibility_dir"
            )
        exe_match = re.search(REGEXP_EXE, full_command)
        if not exe_match:
            logger.warning("Failed to parse game executable from command line.")
            # raise RuntimeError(
            #     "Game executable pattern did not match the command line."
            # )
        data.cmd_steam_game_exe = exe_match and exe_match.group("gameexe")
        data.cmd_steam_game_args = exe_match and exe_match.group("gameargs")

    @staticmethod
    def parse_environment_variables(data: SteamEnvironmentData, logger: logging.Logger):
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
            value = os.getenv(environment_variable) or os.getenv(environment_variable.upper())
            if value and (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
            ):
                value = value[1:-1]
            logger.info(
                "From environment variable:   %s=%s", environment_variable, value
            )
            return value

        data.steam_app_id = from_env(ENV_STEAM_APP_ID)
        data.steam_game_id = from_env(ENV_STEAM_GAME_ID)
        data.steam_base_folder = from_env(ENV_STEAM_BASE_FOLDER)
        data.steam_compat_app_id = from_env(ENV_STEAM_COMPAT_APP_ID)
        data.steam_compat_install_path = from_env(ENV_STEAM_COMPAT_INSTALL_PATH)
        data.steam_compat_data_path = from_env(ENV_STEAM_COMPAT_DATA_PATH)
        data.steam_compat_client_install_path = from_env(
            ENV_STEAM_COMPAT_CLIENT_INSTALL_PATH
        )
        # Store all relevant environment variables in a dictionary for potential future use
        data.environment_variables = {
            env: str(os.getenv(env) or os.getenv(env.upper()))
            for env in ENV_LIST
            if os.getenv(env) or os.getenv(env.upper()) is not None
        }

    @staticmethod
    def restore_environment(data: SteamEnvironmentData, logger: logging.Logger) -> None:
        """
        Restores Steam environment data from a JSON file if it exists.
        """
        if not data.steam_game_id:
            return
        file = GAME_ENVIRONMENT_FILE_TEMPLATE.format(data.steam_game_id)
        if not os.path.isfile(file):
            return

        def restore_value(
            value: str | None, msg: str, env_variable: str | None = None
        ) -> str | None:
            if value:
                logger.info("Restored %s: %s", msg, value)
                if env_variable:
                    logger.info(
                        "Setting environment variable: %s=%s", env_variable, value
                    )
                    os.environ[env_variable] = value
            return value

        with open(file, "r", encoding="utf-8") as f:
            restored_data = json.load(f)
            restored = SteamEnvironmentData(**restored_data)
            data.steam_app_id = data.steam_app_id or restore_value(
                restored.steam_app_id, "Steam App ID", ENV_STEAM_APP_ID
            )
            data.steam_base_folder = data.steam_base_folder or restore_value(
                restored.steam_base_folder, "Steam Base Folder", ENV_STEAM_BASE_FOLDER
            )
            data.steam_compat_install_path = (
                data.steam_compat_install_path
                or restore_value(
                    restored.steam_compat_install_path,
                    "Steam Compatibility Install Path",
                    ENV_STEAM_COMPAT_INSTALL_PATH,
                )
            )
            data.steam_compat_app_id = data.steam_compat_app_id or restore_value(
                restored.steam_compat_app_id,
                "Steam Compatibility App ID",
                ENV_STEAM_COMPAT_APP_ID,
            )
            data.steam_compat_data_path = data.steam_compat_data_path or restore_value(
                restored.steam_compat_data_path,
                "Steam Compatibility Data Path",
                ENV_STEAM_COMPAT_DATA_PATH,
            )
            data.steam_compat_client_install_path = (
                data.steam_compat_client_install_path
                or restore_value(
                    restored.steam_compat_client_install_path,
                    "Steam Compatibility Client Install Path",
                    ENV_STEAM_COMPAT_CLIENT_INSTALL_PATH,
                )
            )
            data.cmd_steam_wrapper = data.cmd_steam_wrapper or restore_value(
                restored.cmd_steam_wrapper, "Steam Wrapper Command"
            )
            data.cmd_steam_reaper = data.cmd_steam_reaper or restore_value(
                restored.cmd_steam_reaper, "Steam Reaper Command"
            )
            data.cmd_steam_sniper = data.cmd_steam_sniper or restore_value(
                restored.cmd_steam_sniper, "Steam Sniper Command"
            )
            data.cmd_steam_compatibility_command = (
                data.cmd_steam_compatibility_command
                or restore_value(
                    restored.cmd_steam_compatibility_command,
                    "Steam Compatibility Command",
                )
            )
            data.cmd_steam_compatibility_tool = (
                data.cmd_steam_compatibility_tool
                or restore_value(
                    restored.cmd_steam_compatibility_tool, "Steam Compatibility Tool"
                )
            )
            data.cmd_steam_compatibility_tools_path = (
                data.cmd_steam_compatibility_tools_path
                or restore_value(
                    restored.cmd_steam_compatibility_tools_path,
                    "Steam Compatibility Tools Path",
                )
            )
            data.cmd_steam_game_exe = data.cmd_steam_game_exe or restore_value(
                restored.cmd_steam_game_exe, "Steam Game Executable"
            )
            data.cmd_steam_game_args = data.cmd_steam_game_args or restore_value(
                restored.cmd_steam_game_args, "Steam Game Arguments"
            )
            data.environment_variables = (
                data.environment_variables or restored.environment_variables
            )

    @classmethod
    def parse(
        cls, data: SteamEnvironmentData, full_command: str, logger: logging.Logger
    ) -> None:
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
        cls.parse_steam_command(full_command, data, logger)
        cls.parse_environment_variables(data, logger)
        cls.restore_environment(data, logger)

    @staticmethod
    def save(data: SteamEnvironmentData, dry_run: bool, logger: logging.Logger) -> None:
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
        FileSystem.dump_as_json(
            data.__dict__,
            GAME_ENVIRONMENT_FILE_TEMPLATE.format(data.steam_game_id),
            dry_run,
            logger,
        )
