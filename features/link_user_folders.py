"""
Feature to link user folders to specified locations to manage saved games and settings.
"""

from typing import override
from core import ConfigurationProperty, FeatureProvider, RuntimeConfiguration
from core.config_storage import ConfigStorage
from core.defaults import LOG_DRY_RUN, PUBLIC_USER_FOLDER_NAME, STEAM_USER_FOLDER_NAME
from core.file_operations import create_symbolic_link

LINK_STEAM_USER_FOLDER_PROPERTY = ConfigurationProperty(
    str,
    "LINK_STEAM_USER_FOLDER",
    "If provided links the steam user folder to the given location",
)

LINK_PUBLIC_USER_FOLDER_PROPERTY = ConfigurationProperty(
    str,
    "LINK_PUBLIC_USER_FOLDER",
    "If provided links the public user folder to the given location",
)

LINK_SHOULD_BACKUP_FOLDERS_PROPERTY = ConfigurationProperty(
    bool,
    "LINK_SHOULD_BACKUP_FOLDERS",
    "If true, backups the user folders before linking them",
    True,
)


class LinkUserFolders(FeatureProvider):
    """
    A feature to manage user folder links for saved games and settings.

    This class provides functionality to link specific user folders, such as the Steam
    user folder and the public user folder, to specified locations for better
    organization and management.
    """

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(
            "Link User Folders",
            [
                LINK_STEAM_USER_FOLDER_PROPERTY,
                LINK_PUBLIC_USER_FOLDER_PROPERTY,
                LINK_SHOULD_BACKUP_FOLDERS_PROPERTY,
            ],
            "Data Management",
        )
        self.config_storage = config_storage

    @override
    def execute_in_pipeline(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        if not runtime_configuration.prefix_path:
            self.logger.warning(
                "No prefix path set in runtime configuration, skipping user folder linking."
            )
            return
        should_backup = LINK_SHOULD_BACKUP_FOLDERS_PROPERTY.get(configuration, True)
        user_folder = LINK_STEAM_USER_FOLDER_PROPERTY.get(configuration)
        if user_folder:
            self.logger.info("Linking user folder to: %s", user_folder)
            prefix_user_folder = (
                f"{runtime_configuration.prefix_path}/{STEAM_USER_FOLDER_NAME}"
            )
            if runtime_configuration.dry_run:
                self.logger.info(
                    LOG_DRY_RUN.format("Ensure user folder link at: %s to: %s"),
                    prefix_user_folder,
                    user_folder,
                )
            else:
                create_symbolic_link(
                    user_folder,
                    prefix_user_folder,
                    self.logger,
                    should_backup=should_backup,
                )
        public_user_folder = LINK_PUBLIC_USER_FOLDER_PROPERTY.get(configuration)
        if public_user_folder:
            self.logger.info("Linking public folder to: %s", public_user_folder)
            prefix_public_user_folder = (
                f"{runtime_configuration.prefix_path}/{PUBLIC_USER_FOLDER_NAME}"
            )
            if runtime_configuration.dry_run:
                self.logger.info(
                    LOG_DRY_RUN.format("Ensure public folder link at: %s to: %s"),
                    prefix_public_user_folder,
                    public_user_folder,
                )
            else:
                create_symbolic_link(
                    public_user_folder,
                    prefix_public_user_folder,
                    self.logger,
                )
