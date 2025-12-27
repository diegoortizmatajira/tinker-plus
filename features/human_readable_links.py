"""Module providing human-readable links feature."""

import os
from typing import override

from core import log_storage
from core.configuration_types import ConfigurationDictionary
from core.defaults import (
    APP_LAST_RUN_LOG_FILE,
    GAME_CONFIG_FILE_TEMPLATE,
    GAME_LOGS_DIR_TEMPLATE,
    GAME_SCRIPT_TEMPLATE,
    HUMAN_READABLE_LINKS_DIR_TEMPLATE,
    LAST_RUN_LOG_FILE,
)
from core.feature_provider import FeatureProvider
from core.file_operations import create_symbolic_link
from core.runtime_configuration import RuntimeConfiguration


class HumanReadableLinks(FeatureProvider):
    """
    Feature provider that creates human-readable symbolic links for game configurations,
    logs, scripts, and game files based on the game's name extracted from the Steam manifest.
    """

    def __init__(self):
        super().__init__("Human Links", [], "UI")

    @override
    def before_execution(
        self,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        if (
            not runtime_configuration.game_executable_command
            or not runtime_configuration.game_executable_command.command
        ):
            return
        try:
            self.logger.info("Current game info: %s", runtime_configuration.game_info)
            game_links_dir = HUMAN_READABLE_LINKS_DIR_TEMPLATE.format(
                runtime_configuration.game_info.name
            )
            os.makedirs(game_links_dir, exist_ok=True)
            # Create symbolic link to the game configuration file
            config_file = GAME_CONFIG_FILE_TEMPLATE.format(
                runtime_configuration.get_game_identifier()
            )
            create_symbolic_link(
                config_file, f"{game_links_dir}/config.json", self.logger
            )

            # Create link to Log Directory
            log_dir = GAME_LOGS_DIR_TEMPLATE.format(
                runtime_configuration.get_game_identifier()
            )
            create_symbolic_link(log_dir, f"{game_links_dir}/logs", self.logger)

            # Create link to Script File
            script_file = GAME_SCRIPT_TEMPLATE.format(
                runtime_configuration.get_game_identifier()
            )
            create_symbolic_link(
                script_file, f"{game_links_dir}/launch_script.sh", self.logger
            )

            # Create link to the Game Files
            if runtime_configuration.steam_environment_data.steam_compat_install_path:
                create_symbolic_link(
                    runtime_configuration.steam_environment_data.steam_compat_install_path,
                    f"{game_links_dir}/game_files",
                    self.logger,
                )

            # Create link to the Game compat data folder
            if runtime_configuration.steam_environment_data.steam_compat_data_path:
                create_symbolic_link(
                    runtime_configuration.steam_environment_data.steam_compat_data_path,
                    f"{game_links_dir}/compat_data",
                    self.logger,
                )

            # Create link to the last run log
            last_run_log = log_storage.LogFactory.singleton().get_log_filename(
                APP_LAST_RUN_LOG_FILE
            )
            create_symbolic_link(last_run_log, LAST_RUN_LOG_FILE, self.logger)

        except RuntimeError as e:
            self.logger.warning("Could not create some human-readable links: %s", e)
