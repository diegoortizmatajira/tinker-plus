"""
The RuntimeProvider module is responsible executing the game using the appropriate
runtime configuration. It manages the merging of global and game-specific settings,
as well as feature-specific customizations to build a comprehensive runtime environment.
"""

import json
from typing import final

from core.compat_tool_info import CompatToolInfo
from core.config_storage import ConfigStorage
from core.configuration_types import ConfigurationDictionary
from core.defaults import LOG_STAGE_STARTED
from core.game_info import GameInfo
from core.steam import get_game_info, parse_steam_command
from core.steam_environment_data import SteamEnvironmentData
from .runtime_configuration import RuntimeConfiguration
from .feature_provider import FeatureAction, FeatureProvider
from .log_storage import LogFactory

EMPTY = "(not provided)"


def unquote(s: str | None) -> str | None:
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


@final
class RuntimeProvider:
    """
    The RuntimeProvider is responsible for managing the runtime configuration and operations.

    This class initializes and builds the runtime configuration by merging global
    and game-specific settings, as well as feature-specific customizations. It also
    manages the execution of the runtime environment using the built configuration.

    Attributes:
        configuration (dict): The merged runtime configuration containing global,
            game-specific, and feature-specific settings.
        runtime_configuration (RuntimeConfiguration | None): The active runtime
            configuration used for executing the environment. Defaults to None.
        features (list[FeatureProvider]): A list of feature providers that contribute
            to building the runtime configuration.
    """

    def __init__(
        self,
        game_command: list[str],
        dry_run: bool,
        features: list[FeatureProvider],
        config_storage: ConfigStorage,
    ):
        self.logger = LogFactory.singleton().get_logger(self.__class__.__name__)
        self.configuration: ConfigurationDictionary = {}
        self.features = features
        self.config_storage = config_storage
        self.runtime_configuration = RuntimeConfiguration(
            game_command,
            GameInfo.empty(),
            SteamEnvironmentData.empty(),
            dry_run=dry_run,
        )
        self.parse_command()
        self.last_applied_configuration: ConfigurationDictionary = {}

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
            _ = CompatToolInfo.scan_and_populate_cache(
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
            self.logger.info(
                "No configuration changes detected, skipping re-application."
            )
            return

        self.runtime_configuration.reset()
        for feature in self.features:
            _ = feature.try_apply_configuration(
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

    def get_available_actions(self) -> list[FeatureAction]:
        """
        Lists all available actions provided by the feature providers.

        This method iterates through the list of feature providers and collects
        their available actions into a single list.

        Returns:
            list[FeatureProvider]: A list of all available feature providers.
        """
        available_actions: list[FeatureAction] = []
        for feature in self.features:
            available_actions.extend(feature.actions)
        return available_actions
