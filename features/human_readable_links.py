"""Module providing human-readable links feature."""

import os
from typing import override

from core import FeatureProvider, LogFactory
from core.defaults import (
    APP_LAST_RUN_LOG_FILE,
    GAME_CONFIG_FILE_TEMPLATE,
    GAME_ENVIRONMENT_FILE_TEMPLATE,
    GAME_LOGS_DIR_TEMPLATE,
    HUMAN_READABLE_LINKS_DIR_TEMPLATE,
    LAST_RUN_LOG_FILE,
)
from file_system import FileSystem
from model import ConfigurationDictionary, RuntimeConfiguration


class HumanReadableLinks(FeatureProvider):
    """
    Feature provider that creates human-readable symbolic links for game configurations,
    logs and game files based on the game's name extracted from the Steam manifest.
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
            FileSystem.create_symbolic_link(
                config_file, f"{game_links_dir}/config.json", self.logger
            )
            environment_file = GAME_ENVIRONMENT_FILE_TEMPLATE.format(
                runtime_configuration.get_game_identifier()
            )
            FileSystem.create_symbolic_link(
                environment_file, f"{game_links_dir}/environment.json", self.logger
            )

            # Create link to Log Directory
            log_dir = GAME_LOGS_DIR_TEMPLATE.format(
                runtime_configuration.get_game_identifier()
            )
            FileSystem.create_symbolic_link(
                log_dir, f"{game_links_dir}/logs", self.logger
            )

            # Create link to the Game Files
            game_files_path = runtime_configuration.get_game_files_path()
            if game_files_path:
                FileSystem.create_symbolic_link(
                    game_files_path,
                    f"{game_links_dir}/game_files",
                    self.logger,
                )

            # Create link to the Game compat data folder
            compat_data_path = runtime_configuration.get_compat_data_path()
            if compat_data_path:
                FileSystem.create_symbolic_link(
                    compat_data_path,
                    f"{game_links_dir}/compat_data",
                    self.logger,
                )

            # Create link to the last run log
            last_run_log = LogFactory.singleton().get_log_filename(
                APP_LAST_RUN_LOG_FILE
            )
            FileSystem.create_symbolic_link(
                last_run_log, LAST_RUN_LOG_FILE, self.logger
            )

        except RuntimeError as e:
            self.logger.warning("Could not create some human-readable links: %s", e)
