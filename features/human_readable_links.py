"""Module providing human-readable links feature."""

import os
from pathlib import Path
from typing import override
from core.defaults import (
    GAME_CONFIG_FILE_TEMPLATE,
    GAME_LOGS_DIR_TEMPLATE,
    GAME_SCRIPT_TEMPLATE,
    HUMAN_READABLE_LINKS_DIR_TEMPLATE,
)
from core.feature_provider import FeatureProvider
from core.file_operations import create_symbolic_link
from core.runtime_configuration import RuntimeConfiguration


class HumanReadableLinks(FeatureProvider):
    def __init__(self):
        super().__init__([])

    @override
    def execute_in_pipeline(
        self, _configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        if not runtime_configuration.steam_game_exe:
            return
        try:
            exe = Path(runtime_configuration.steam_game_exe)
            game_name = exe.stem
            game_links_dir = HUMAN_READABLE_LINKS_DIR_TEMPLATE.format(game_name)
            os.makedirs(game_links_dir, exist_ok=True)
            # Create symbolic link to the game configuration file
            config_file = GAME_CONFIG_FILE_TEMPLATE.format(
                runtime_configuration.steam_game_id
            )
            create_symbolic_link(
                config_file, f"{game_links_dir}/config.json", self.logger
            )

            # Create link to Log Directory
            log_dir = GAME_LOGS_DIR_TEMPLATE.format(runtime_configuration.steam_game_id)
            create_symbolic_link(log_dir, f"{game_links_dir}/logs", self.logger)

            # Create link to Script File
            script_file = GAME_SCRIPT_TEMPLATE.format(
                runtime_configuration.steam_game_id
            )
            create_symbolic_link(
                script_file, f"{game_links_dir}/launch_script.sh", self.logger
            )

            # Create link to the Game Files
            if runtime_configuration.steam_compat_install_path:
                create_symbolic_link(
                    runtime_configuration.steam_compat_install_path,
                    f"{game_links_dir}/game_files",
                    self.logger,
                )

            # Create link to the Game compat data folder
            if runtime_configuration.steam_compat_data_path:
                create_symbolic_link(
                    runtime_configuration.steam_compat_data_path,
                    f"{game_links_dir}/compat_data",
                    self.logger,
                )
        except RuntimeError as e:
            self.logger.warning("Could not create some human-readable links: %s", e)
