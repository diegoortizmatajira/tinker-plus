"""Feature to back up game files to a specified location."""

from pathlib import Path
from typing import Any
from core.configuration_property import ConfigurationProperty
from core.defaults import LOG_DRY_RUN
from core.feature_provider import FeatureAction, FeatureProvider
from core.process_runner import run_command
from core.runtime_configuration import ExecutableCommand, RuntimeConfiguration

BACKUP_LOCATION_PROPERTY = ConfigurationProperty(
    str,
    "BACKUP_LOCATION",
    "Backup Location",
    "The location where game files are backed up",
)


class GameFilesBackup(FeatureProvider):
    """Feature provider for backing up and restoring game files.

    This class facilitates the process of backing up game files to a specified location
    and restoring them from that location. It defines actions for both backup and
    restoration, leveraging provided runtime configurations and commands.
    """

    def __init__(self):
        super().__init__(
            "Game Files Backup",
            [
                BACKUP_LOCATION_PROPERTY,
            ],
            "Data Management",
            actions=[
                FeatureAction(
                    "Backup Game Files",
                    "Backs up game files to the specified location.",
                    self.backup_game_files,
                ),
                FeatureAction(
                    "Restore Game Files",
                    "Restores game files from the backup location.",
                    self.restore_game_files,
                ),
            ],
        )

    def __get_backup_archive_name(
        self, configuration: dict[str, Any], runtime_configuration: RuntimeConfiguration
    ):
        backup_location = BACKUP_LOCATION_PROPERTY.get_or_fail(configuration)
        archive_name = f"{backup_location}/{runtime_configuration.steam_game_id}.7z"
        return archive_name

    def backup_game_files(
        self, configuration: dict[str, Any], runtime_configuration: RuntimeConfiguration
    ):
        """Backs up game files to a specified location.

        Args:
            configuration (dict[str, Any]): The configuration dictionary containing backup settings.
            runtime_configuration (RuntimeConfiguration): The runtime
            configuration, providing game paths and options.

        Returns:
            None
        """
        game_files_location = runtime_configuration.steam_compat_install_path
        archive_name = self.__get_backup_archive_name(
            configuration, runtime_configuration
        )
        command = ExecutableCommand(
            "7za",
            f'a -m0=lzma2 -mx=9 -mmt8 "{archive_name}" "{game_files_location}"',
        )
        if runtime_configuration.dry_run:
            self.logger.info(LOG_DRY_RUN.format("Backup command: %s"), command)
            return
        process = run_command(command, self.logger)
        if process:
            with process:
                self.logger.info(
                    "Backing up game files from %s to %s...",
                    game_files_location,
                    archive_name,
                )
                process.wait()
                self.logger.info(
                    "Game files backed up to %s successfully.", archive_name
                )

    def restore_game_files(
        self, configuration: dict[str, Any], runtime_configuration: RuntimeConfiguration
    ):
        """Restores game files from the backup location.

        Args:
            configuration (dict[str, Any]): The configuration dictionary
            containing restore settings.
            runtime_configuration (RuntimeConfiguration): The runtime
            configuration, providing game paths and options.

        Returns:
            None
        """
        if not runtime_configuration.steam_compat_install_path:
            self.logger.warning(
                "Steam compatibility install path is not set. Cannot restore game files."
            )
            return
        # Get the parent directory of the Steam compatibility install path
        game_files_location = Path(
            runtime_configuration.steam_compat_install_path
        ).parent
        archive_name = self.__get_backup_archive_name(
            configuration, runtime_configuration
        )
        command = ExecutableCommand(
            "7za",
            f'x -o"{game_files_location}" "{archive_name}"',
        )
        if runtime_configuration.dry_run:
            self.logger.info(LOG_DRY_RUN.format("Restore command: %s"), command)
            return
        process = run_command(command, self.logger)
        if process:
            with process:
                self.logger.info(
                    "Restoring up game files from %s to %s...",
                    archive_name,
                    game_files_location,
                )
                process.wait()
                self.logger.info(
                    "Game files restored up to %s successfully.", game_files_location
                )
