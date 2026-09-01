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

    def _link_folder(
        self,
        label: str,
        source: str,
        destination: str,
        should_backup: bool,
        dry_run: bool,
    ):
        """Links `source` into `destination` under the Wine prefix, or logs the
        intended link when `dry_run` is enabled.

        Args:
            label (str): Human-readable name of the folder being linked, used
                in log messages (e.g. "user", "public", "custom").
            source (str): Path to link from.
            destination (str): Path inside the Wine prefix to create the link at.
            should_backup (bool): Whether to back up an existing folder before
                replacing it (forwarded to `FileSystem.create_symbolic_link`).
            dry_run (bool): If True, logs the intended link instead of performing it.
        """
        self.logger.info("Linking %s folder from: %s to: %s", label, source, destination)
        if dry_run:
            self.logger.info(
                LOG_DRY_RUN.format(f"Ensure {label} folder link at: %s to: %s"),
                destination,
                source,
            )
        else:
            FileSystem.create_symbolic_link(
                source,
                destination,
                self.logger,
                should_backup=should_backup,
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
        dry_run = runtime_configuration.dry_run

        user_folder = LINK_STEAM_USER_FOLDER_PROPERTY.get(configuration)
        if user_folder:
            self._link_folder(
                "user",
                user_folder,
                f"{runtime_configuration.prefix_path}/{STEAM_USER_FOLDER_NAME}",
                should_backup,
                dry_run,
            )

        public_user_folder = LINK_PUBLIC_USER_FOLDER_PROPERTY.get(configuration)
        if public_user_folder:
            self._link_folder(
                "public",
                public_user_folder,
                f"{runtime_configuration.prefix_path}/{PUBLIC_USER_FOLDER_NAME}",
                should_backup,
                dry_run,
            )

        custom_source = LINK_CUSTOM_SOURCE_PROPERTY.get(configuration)
        custom_destination = LINK_CUSTOM_DESTINATION_PROPERTY.get(configuration)
        if custom_source and custom_destination:
            prefix_custom_destination = f"{runtime_configuration.prefix_path}/{DRIVE_C_DIR_NAME}/{custom_destination}"
            self._link_folder(
                "custom",
                custom_source,
                prefix_custom_destination,
                should_backup,
                dry_run,
            )
