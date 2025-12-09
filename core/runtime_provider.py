"""
The RuntimeProvider module is responsible executing the game using the appropriate
runtime configuration. It manages the merging of global and game-specific settings,
as well as feature-specific customizations to build a comprehensive runtime environment.
"""

import json
import os

from typing import List, Optional

from core.compat_tool_info import CompatToolInfo
from core.config_storage import ConfigStorage
from core.defaults import LOG_STAGE_STARTED
from core.game_info import GameInfo
from core.steam import get_game_info, parse_steam_command
from .runtime_configuration import RuntimeConfiguration
from .feature_provider import FeatureAction, FeatureProvider
from .log_storage import LogFactory

EMPTY = "(not provided)"


def unquote(s: Optional[str]) -> Optional[str]:
    """
    Removes surrounding quotes from a string, if present.

    Args:
        s (str): The input string that may have surrounding quotes.

    Returns:
        str: The string with surrounding quotes removed, or the original string
        if no surrounding quotes are present.
    """
    if s and (
        (s.startswith('"') and s.endswith('"'))
        or (s.startswith("'") and s.endswith("'"))
    ):
        return s[1:-1]
    return s


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
        self,
        game_command: List[str],
        dry_run: bool,
        features: List[FeatureProvider],
        config_storage: ConfigStorage,
    ):
        self.logger = LogFactory.singleton().get_logger(self.__class__.__name__)
        self.configuration: dict = {}
        self.features = features
        self.config_storage = config_storage
        self.runtime_configuration = RuntimeConfiguration(
            game_command, GameInfo.empty(), dry_run
        )
        self.read_steam_environment()
        self.parse_command()
        self.runtime_configuration.game_info = get_game_info(
            self.runtime_configuration, self.logger
        )
        self.last_applied_configuration: dict = {}

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
            parse_steam_command(self.runtime_configuration)
            # Ensure CompatToolInfo is cached
            if self.runtime_configuration.steam_compatibility_tool:
                compat_tool_info = CompatToolInfo.from_cache(
                    self.runtime_configuration.steam_compatibility_tool, self.logger
                )
                if not compat_tool_info:
                    compat_tool_info = CompatToolInfo(
                        name=self.runtime_configuration.steam_compatibility_tool,
                        dir=self.runtime_configuration.steam_compatibility_tools_path
                        or "",
                    )
                    compat_tool_info.put_in_cache(self.logger)
            CompatToolInfo.scan_and_populate_cache(
                self.logger, self.runtime_configuration
            )
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
            unquote(os.getenv("SteamAppId")) or self.runtime_configuration.steam_app_id
        )
        self.logger.info(
            "Steam App ID: %s", self.runtime_configuration.steam_app_id or EMPTY
        )
        self.runtime_configuration.steam_game_id = (
            unquote(os.getenv("SteamGameId"))
            or self.runtime_configuration.steam_game_id
        )
        self.logger.info(
            "Steam Game ID: %s", self.runtime_configuration.steam_game_id or EMPTY
        )
        self.runtime_configuration.steam_base_folder = (
            unquote(os.getenv("STEAM_BASE_FOLDER"))
            or self.runtime_configuration.steam_base_folder
        )
        self.logger.info(
            "Steam Base Folder: %s",
            self.runtime_configuration.steam_base_folder or EMPTY,
        )
        self.runtime_configuration.steam_compat_install_path = (
            unquote(os.getenv("STEAM_COMPAT_INSTALL_PATH"))
            or self.runtime_configuration.steam_compat_install_path
        )
        self.logger.info(
            "Steam Compat Install Path: %s",
            self.runtime_configuration.steam_compat_install_path or EMPTY,
        )
        self.runtime_configuration.steam_compat_data_path = (
            unquote(os.getenv("STEAM_COMPAT_DATA_PATH"))
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

    def build_configuration(self, pre_apply_configuration: bool = False):
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
        self.logger.info(LOG_STAGE_STARTED.format("Build Configuration Stage."))
        # Fills any missing configuration with defaults from features
        for feature in self.features:
            self.configuration = feature.build_configuration(
                self.configuration,
                self.runtime_configuration,
            )
        # Override configuration if needed
        for feature in self.features:
            self.configuration = feature.override_configuration(
                self.configuration,
                self.runtime_configuration,
            )
        if pre_apply_configuration:
            self.logger.info(
                LOG_STAGE_STARTED.format("Pre-Applying Configuration Stage.")
            )
            self.__apply_feature_configurations()

    def __apply_feature_configurations(self):
        # Compare with last applied configuration to avoid re-applying
        if json.dumps(self.last_applied_configuration, sort_keys=True) == json.dumps(
            self.configuration, sort_keys=True
        ):
            self.logger.info("No configuration changes detected, skipping re-application.")
            return

        self.runtime_configuration.reset()
        for feature in self.features:
            feature.try_apply_configuration(
                self.configuration, self.runtime_configuration
            )
        self.last_applied_configuration = self.configuration.copy()

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
        self.logger.info(LOG_STAGE_STARTED.format("Apply Configuration Stage."))
        # Apply configurations to runtime
        self.__apply_feature_configurations()
        self.runtime_configuration.execute_trainers = run_with_trainers

        self.logger.info(LOG_STAGE_STARTED.format("Before Execution Stage."))
        for features in self.features:
            features.before_execution(self.configuration, self.runtime_configuration)

        self.logger.info(LOG_STAGE_STARTED.format("Pipeline Execution Stage."))
        for features in self.features:
            features.execute_in_pipeline(self.configuration, self.runtime_configuration)

        self.logger.info(LOG_STAGE_STARTED.format("After Execution Stage."))
        for features in self.features:
            features.after_execution(self.configuration, self.runtime_configuration)

    def run_action(self, action: FeatureAction):
        """
        Executes a specific feature action using the current runtime configuration.

        This method first builds the runtime configuration, applies necessary
        feature configurations, and then executes the provided action within the
        runtime environment. The action being executed is logged for tracking.

        Args:
            action (FeatureAction): The specific feature action to execute, which
                defines its own behavior within the runtime environment.

        Logs:
            - Logs the execution stage and the status of the action being executed.
        """
        self.__apply_feature_configurations()
        self.logger.info(LOG_STAGE_STARTED.format(f"Executing Action: {action.name}"))
        action.action(self.configuration, self.runtime_configuration)
        self.logger.info("Action '%s' executed successfully.", action.name)

    def get_available_actions(self) -> List[FeatureAction]:
        """
        Lists all available actions provided by the feature providers.

        This method iterates through the list of feature providers and collects
        their available actions into a single list.

        Returns:
            List[FeatureProvider]: A list of all available feature providers.
        """
        available_actions: List[FeatureAction] = []
        for feature in self.features:
            available_actions.extend(feature.actions)
        return available_actions
