"""
Feature to link user folders to specified locations to manage saved games and settings.
"""

from typing import override

from core import FeatureProvider
from defaults import (
    DRIVE_C_DIR_NAME,
    LOG_DRY_RUN,
    PUBLIC_USER_FOLDER_NAME,
    STEAM_USER_FOLDER_NAME,
)
from file_system import FileSystem
from model import ConfigurationProperty, RuntimeConfiguration, ConfigurationDictionary

LINK_STEAM_USER_FOLDER_PROPERTY = ConfigurationProperty(
    str,
    "LINK_STEAM_USER_FOLDER",
    "Path to Steam User Folder",
    "If provided links the steam user folder to the given location",
)

LINK_PUBLIC_USER_FOLDER_PROPERTY = ConfigurationProperty(
    str,
    "LINK_PUBLIC_USER_FOLDER",
    "Path to Public User Folder",
    "If provided links the public user folder to the given location",
)

LINK_SHOULD_BACKUP_FOLDERS_PROPERTY = ConfigurationProperty(
    bool,
    "LINK_SHOULD_BACKUP_FOLDERS",
    "Backup User Folders",
    "If true, backups the user folders before linking them",
    True,
)

LINK_CUSTOM_SOURCE_PROPERTY = ConfigurationProperty(
    str,
    "LINK_CUSTOM_SOURCE",
    "Custom Source Folder",
    "If provided, links a custom source folder to the prefix",
)

LINK_CUSTOM_DESTINATION_PROPERTY = ConfigurationProperty(
    str,
    "LINK_CUSTOM_DESTINATION",
    "Custom Destination Folder",
    "If provided, links to a custom destination folder in the prefix",
)


class LinkUserFolders(FeatureProvider):
    """
    A feature to manage user folder links for saved games and settings.

    This class provides functionality to link specific user folders, such as the Steam
    user folder and the public user folder, to specified locations for better
    organization and management.
    """

    def __init__(self):
        super().__init__(
            "Link User Folders",
            [
                LINK_STEAM_USER_FOLDER_PROPERTY,
                LINK_PUBLIC_USER_FOLDER_PROPERTY,
                LINK_SHOULD_BACKUP_FOLDERS_PROPERTY,
                LINK_CUSTOM_SOURCE_PROPERTY,
                LINK_CUSTOM_DESTINATION_PROPERTY,
            ],
            "Data Management",
        )

    @override
    def before_execution(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        """Links the configured Steam user, public user, and custom folders into
        the Wine prefix, optionally backing up any existing folder being replaced."""
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
                FileSystem.create_symbolic_link(
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
                FileSystem.create_symbolic_link(
                    public_user_folder,
                    prefix_public_user_folder,
                    self.logger,
                )
        custom_source = LINK_CUSTOM_SOURCE_PROPERTY.get(configuration)
        custom_destination = LINK_CUSTOM_DESTINATION_PROPERTY.get(configuration)
        if custom_source and custom_destination:
            prefix_custom_destination = f"{runtime_configuration.prefix_path}/{DRIVE_C_DIR_NAME}/{custom_destination}"
            self.logger.info(
                "Linking custom folder from: %s to: %s",
                custom_source,
                prefix_custom_destination,
            )
            if runtime_configuration.dry_run:
                self.logger.info(
                    LOG_DRY_RUN.format("Ensure custom link at: %s to: %s"),
                    prefix_custom_destination,
                    custom_source,
                )
            else:
                FileSystem.create_symbolic_link(
                    custom_source,
                    prefix_custom_destination,
                    self.logger,
                )
