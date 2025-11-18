"""
The RuntimeProvider module is responsible executing the game using the appropriate
runtime configuration. It manages the merging of global and game-specific settings,
as well as feature-specific customizations to build a comprehensive runtime environment.
"""

import os
import re

from typing import List
from .runtime_configuration import RuntimeConfiguration
from .feature_provider import FeatureProvider
from .log_storage import logger_factory

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
    full_pattern = (
        r"^(?P<othercommands>(\S+\s+)+)?"
        r"(?P<stlwrapper>\S+steam-launch-wrapper)\s+"
        r"(?P<reaper>\S+reaper)\s+"
        r".+?(--)?\s+"
        r"(?P<sniper>\S+sniper\S+(\s+--\w+=.+)+)\s+"
        r"--\s+"
        r"(?P<compatibility>"
        r"(?P<compatibility_dir>\S+compatibilitytools\.d)/"
        r"(?P<compatibility_tool>\S+)/\S+\swaitforexitandrun)\s+"
        r"(?P<gameexe>.*)$"
    )

    match = re.search(full_pattern, " ".join(runtime_configuration.original_command))
    if not match:
        raise RuntimeError("Pattern did not match the command line.")

    runtime_configuration.steam_other_wrapper_commands = match.group("othercommands")
    runtime_configuration.steam_wrapper = match.group("stlwrapper")
    runtime_configuration.steam_reaper = match.group("reaper")
    runtime_configuration.steam_sniper = match.group("sniper")
    runtime_configuration.steam_compatibility_command = match.group("compatibility")
    runtime_configuration.steam_compatibility_tool = match.group("compatibility_tool")
    runtime_configuration.steam_compatibility_tools_path = match.group(
        "compatibility_dir"
    )
    runtime_configuration.steam_game_exe = match.group("gameexe")


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
        self.logger = logger_factory.get_logger(self.__class__.__name__)
        self.configuration: dict = {}
        self.features = features
        self.runtime_configuration = RuntimeConfiguration(game_command, dry_run)
        self.read_steam_environment()
        self.parse_command()

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
            "Steam Other Wrapper Commands: %s",
            self.runtime_configuration.steam_other_wrapper_commands,
        )
        self.logger.info(
            "Steam Launch Wrapper: %s", self.runtime_configuration.steam_wrapper
        )
        self.logger.info(
            "Steam Reaper Command: %s", self.runtime_configuration.steam_reaper
        )
        self.logger.info(
            "Steam Sniper Command: %s", self.runtime_configuration.steam_sniper
        )
        self.logger.info(
            "Steam Compatibility Tool Command: %s",
            self.runtime_configuration.steam_compatibility_command,
        )
        self.logger.info(
            "Steam Compatibility Tool: %s",
            self.runtime_configuration.steam_compatibility_tool,
        )
        self.logger.info(
            "Steam Compatibility Tools path: %s",
            self.runtime_configuration.steam_compatibility_tools_path,
        )
        self.logger.info(
            "Steam Game Executable: %s", self.runtime_configuration.steam_game_exe
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
        self.runtime_configuration.prefix_path = (
            f"{self.runtime_configuration.steam_compat_data_path}/pfx"
        )

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
                self.runtime_configuration.steam_game_id or "unknown",
                self.runtime_configuration.steam_app_id or "unknown",
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
        # Apply configurations to runtime
        for feature in self.features:
            feature.try_apply_configuration(
                self.configuration, self.runtime_configuration
            )

        self.runtime_configuration.execute_trainers = run_with_trainers

        for features in self.features:
            features.execute_in_pipeline(self.configuration, self.runtime_configuration)
