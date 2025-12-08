"""Module defining the abstract base class for command handlers."""

from abc import ABC, abstractmethod
import logging
from typing import List

from core.config_storage import ConfigStorage
from core.runtime_provider import RuntimeProvider
from features.compat_data_folders import CompatDataFolders
from features.context_commands import ContextCommands
from features.external_tools import ExternalTools
from features.game_files_backup import GameFilesBackup
from features.game_runner import GameRunner
from features.general_runtime import GeneralRuntime
from features.gui_options import CURRENT_GUI_OPTIONS
from features.human_readable_links import HumanReadableLinks
from features.link_user_folders import LinkUserFolders
from features.prefix_selection import PrefixSelection
from features.proton_selection import ProtonSelection
from features.read_config import ReadConfig
from features.sdl_config import SdlConfig
from features.steam_tools import SteamTools
from features.trainer_launch_settings import TrainerLaunchSettings
from features.wine_config import WineConfig
from features.winetricks_install import WinetricksInstall


class BaseHandler(ABC):
    """
    Abstract base class for command handlers.
    """

    @abstractmethod
    def handle(self, _args, _logger: logging.Logger):
        """
        Handles the command with the given arguments and logger.
        """

    def get_runtime_provider(
        self, game_command: List[str], dry_run: bool
    ) -> RuntimeProvider:
        """
        Creates and returns a RuntimeProvider instance configured with
        the necessary features and storage.
        """
        storage = ConfigStorage()
        return RuntimeProvider(
            game_command,
            dry_run,
            # List of feature providers (Order matters as it affects
            # how the command pipeline is built)
            [
                GeneralRuntime(),
                CURRENT_GUI_OPTIONS,
                # Features that run before game launch
                CompatDataFolders(),
                GameFilesBackup(),
                WinetricksInstall(),
                LinkUserFolders(),
                HumanReadableLinks(),
                ContextCommands(),
                # Features that affect run pipeline or game launch
                ExternalTools(),
                SteamTools(),
                ProtonSelection(),
                SdlConfig(),
                WineConfig(),
                PrefixSelection(),
                TrainerLaunchSettings(),
                GameRunner(),
                # ReadConfig and CURRENT_GUI_OPTIONS have to be the last ones
                # to ensure default configs are read first, then overridden by user configs
                ReadConfig(storage),
            ],
            storage,
        )
