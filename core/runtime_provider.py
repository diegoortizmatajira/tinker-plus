"""
The RuntimeProvider module is responsible executing the game using the appropriate
runtime configuration. It manages the merging of global and game-specific settings,
as well as feature-specific customizations to build a comprehensive runtime environment.
"""

import os
from pathlib import Path
import re

from typing import List, Optional

from core.defaults import STEAM_MANIFESTS_TEMPLATE
from core.game_info import GameInfo
from .runtime_configuration import RuntimeConfiguration
from .feature_provider import FeatureProvider
from .log_storage import LogFactory

EMPTY = "(not provided)"


def parse_command(runtime_configuration: RuntimeConfiguration):
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
        r"(?P<compatibility_dir>\/\S+compatibilitytools\.d)/"
        r"(?P<compatibility_tool>\S+)/\S+\swaitforexitandrun)\s+"
    )
    exe_regexp = r"\s(?P<gameexe>(\/[\w\.\s\-]+\w)+\.exe)\s?(?P<gameargs>.*)$"

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
    if not compatibility_match:
        raise RuntimeError("Compatibility tool pattern did not match the command line.")
    runtime_configuration.steam_compatibility_command = compatibility_match.group(
        "compatibility"
    )
    runtime_configuration.steam_compatibility_tool = compatibility_match.group(
        "compatibility_tool"
    )
    runtime_configuration.steam_compatibility_tools_path = compatibility_match.group(
        "compatibility_dir"
    )
    exe_match = re.search(exe_regexp, full_command)
    if not exe_match:
        raise RuntimeError("Game executable pattern did not match the command line.")
    runtime_configuration.steam_game_exe = exe_match.group("gameexe")
    runtime_configuration.steam_game_args = exe_match.group("gameargs")


class RuntimeProvider:
    """
    The RuntimeProvider is responsible for managing the runtime configuration and operations.

    This class initializes and builds the runtime configuration by merging global
    and game-specific settings, as well as feature-specific customizations. It also
    manages the execution of the runtime environment using the built configuration.

    Attributes:
        configuration (dict): The merged runtime configuration containing global,
            game-specific, and feature-specific settings.
        runtime_configuration (Optional[RuntimeConfiguration]): The active runtime
            configuration used for executing the environment. Defaults to None.
        features (List[FeatureProvider]): A list of feature providers that contribute
            to building the runtime configuration.
    """

    def __init__(
        self, game_command: List[str], dry_run: bool, features: List[FeatureProvider]
    ):
        self.logger = LogFactory.singleton().get_logger(self.__class__.__name__)
        self.configuration: dict = {}
        self.features = features
        self.runtime_configuration = RuntimeConfiguration(
            game_command, GameInfo.empty(), dry_run
        )
        self.read_steam_environment()
        self.parse_command()
        self.runtime_configuration.game_info = self.get_game_info()

    def parse_command(self):
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
        self.logger.info(
            "Steam Original Game Command: %s",
            " ".join(self.runtime_configuration.original_command),
        )
        try:
            parse_command(self.runtime_configuration)
        except RuntimeError as e:
            self.logger.warning("Failed to parse the game command line: %s", e)
            return

        self.logger.info(
            "Steam Original Compatibility Tool: %s",
            self.runtime_configuration.steam_compatibility_tool,
        )
        self.logger.info(
            "Steam Original Compatibility Tools path: %s",
            self.runtime_configuration.steam_compatibility_tools_path,
        )
        self.logger.info(
            "Steam Original Game Executable: %s",
            self.runtime_configuration.steam_game_exe,
        )

    def read_steam_environment(self):
        """
        Reads the Steam environment variables and updates the runtime configuration.

        This method retrieves relevant environment variables such as `SteamAppId`,
        `SteamGameId`, `STEAM_COMPAT_INSTALL_PATH`, and `STEAM_COMPAT_DATA_PATH`
        to set up the runtime configuration. It populates missing values with the
        defaults from the runtime configuration instance if the environment variables
        are not available.

        Updates:
            - runtime_configuration.steam_app_id: The Steam application ID.
            - runtime_configuration.steam_game_id: The Steam game ID.
            - runtime_configuration.steam_compat_install_path: The installation path
              for Steam compatibility tools.
            - runtime_configuration.steam_compat_data_path: The data path for Steam
              compatibility tools.
            - runtime_configuration.prefix_path: Derived prefix path based on the
              compatibility data path.

        Logs:
            - Logs the retrieved or default values for each updated configuration field.
        """
        self.runtime_configuration.steam_app_id = (
            os.getenv("SteamAppId") or self.runtime_configuration.steam_app_id
        )
        self.logger.info(
            "Steam App ID: %s", self.runtime_configuration.steam_app_id or EMPTY
        )
        self.runtime_configuration.steam_game_id = (
            os.getenv("SteamGameId") or self.runtime_configuration.steam_game_id
        )
        self.logger.info(
            "Steam Game ID: %s", self.runtime_configuration.steam_game_id or EMPTY
        )
        self.runtime_configuration.steam_base_folder = (
            os.getenv("STEAM_BASE_FOLDER")
            or self.runtime_configuration.steam_base_folder
        )
        self.logger.info(
            "Steam Base Folder: %s",
            self.runtime_configuration.steam_base_folder or EMPTY,
        )
        self.runtime_configuration.steam_compat_install_path = (
            os.getenv("STEAM_COMPAT_INSTALL_PATH")
            or self.runtime_configuration.steam_compat_install_path
        )
        self.logger.info(
            "Steam Compat Install Path: %s",
            self.runtime_configuration.steam_compat_install_path or EMPTY,
        )
        self.runtime_configuration.steam_compat_data_path = (
            os.getenv("STEAM_COMPAT_DATA_PATH")
            or self.runtime_configuration.steam_compat_data_path
        )
        self.logger.info(
            "Steam Compat Data Path: %s",
            self.runtime_configuration.steam_compat_data_path or EMPTY,
        )
        if self.runtime_configuration.steam_compat_data_path:
            self.runtime_configuration.prefix_path = (
                f"{self.runtime_configuration.steam_compat_data_path}/pfx"
            )

    def get_game_info(self) -> GameInfo:
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
            self.runtime_configuration.steam_game_id
            or self.runtime_configuration.steam_app_id
            or "unknown"
        )
        self.logger.debug("Getting game info for Game ID: %s", game_id)
        game_info = GameInfo.from_cache(game_id, self.logger)
        if game_info:
            self.logger.debug("Found game info in cache: %s", game_info)
            return game_info

        manifest_path = STEAM_MANIFESTS_TEMPLATE.format(
            self.runtime_configuration.steam_base_folder,
            self.runtime_configuration.steam_game_id,
        )
        game_info = GameInfo(
            game_id=game_id,
            name=Path(self.runtime_configuration.steam_game_exe or "unknown").stem,
        )
        self.logger.debug("Looking for Steam manifest at: %s", manifest_path)
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as manifest_file:
                    for line in manifest_file:
                        if '"name"' in line:
                            # Extract the game name from the line
                            name = line.split('"')[3]
                            game_info.name = name
            except Exception as e:
                self.logger.warning(
                    "An error occurred while reading the Steam manifest file: %s", e
                )
        else:
            self.logger.warning(
                "Steam manifest file does not exist at: %s", manifest_path
            )
        game_info.put_in_cache(self.logger)
        # Fallback to using the executable name if manifest reading fails
        return game_info

    def build_configuration(self):
        """
        Builds the runtime configuration by merging global and game-specific configurations,
        and applies feature-specific customizations.

        The method performs the following steps:
        - Reads global and game-specific configurations.
        - Merges the configurations.
        - Builds the feature configurations by calling `build_configuration` on each feature.

        Raises:
            RuntimeError: If any critical configuration step fails.
        """
        # Fills any missing configuration with defaults from features
        for feature in self.features:
            self.configuration = feature.build_configuration(
                self.configuration,
                self.runtime_configuration,
            )

    def run(self, run_with_trainers: bool = True):
        """
        Executes the runtime environment using the provided configuration and optional trainers.

        This method applies the prepared runtime configuration to the environment,
        executing all enabled features within the pipeline. It provides an option to
        include or exclude trainers during the runtime execution.

        Args:
            run_with_trainers (bool): A flag indicating whether trainers should be
                executed as part of the runtime environment. Defaults to True.
        """
        self.runtime_configuration.reset()
        # Apply configurations to runtime
        for feature in self.features:
            feature.try_apply_configuration(
                self.configuration, self.runtime_configuration
            )
        self.runtime_configuration.execute_trainers = run_with_trainers

        for features in self.features:
            features.execute_in_pipeline(self.configuration, self.runtime_configuration)
