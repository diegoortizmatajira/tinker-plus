"""Feature to back up game files to a specified location."""

from pathlib import Path
from typing import override
from core import (
    FeatureAction,
    FeatureProvider,
    ProcessRunner,
)
from defaults import LOG_DRY_RUN
from model import ConfigurationProperty, RuntimeConfiguration, ConfigurationDictionary

BACKUP_LOCATION_PROPERTY = ConfigurationProperty(
    str,
    "BACKUP_LOCATION",
    "Backup Location",
    "The location where game files are backed up",
)

BACKUP_RESTORE_IF_NOT_INSTALLED_PROPERTY = ConfigurationProperty(
    bool,
    "BACKUP_RESTORE_IF_NOT_INSTALLED",
    "Restores game files if not found when launching",
    (
        "If enabled, the system will attempt to restore game files from the backup "
        "location if they are not found in the expected installation path when launching the game."
    ),
    False,
)

BACKUP_ARCHIVE_COMMAND_PROPERTY = ConfigurationProperty(
    str,
    "BACKUP_ARCHIVE_COMMAND",
    "Backup archive Command",
    (
        "The command used to create a backup archive of the game files."
        "Use {archive} for the archive path and {source} for the source path."
    ),
    '7za a -y -m0=lzma2 -mx=9 -mmt8 "{archive}" "{source}"',
)

BACKUP_RESTORE_COMMAND_PROPERTY = ConfigurationProperty(
    str,
    "BACKUP_RESTORE_COMMAND",
    "Backup restore Command",
    (
        "The command used to restore game files from the backup archive."
        "Use {archive} for the archive path and {destination} for the destination path."
    ),
    '7za x -y -o"{destination}" "{archive}"',
)

BACKUP_ARCHIVE_NAME_TEMPLATE_PROPERTY = ConfigurationProperty(
    str,
    "BACKUP_ARCHIVE_NAME_TEMPLATE",
    "Backup Archive Name Template",
    (
        "Template for naming the backup archive files."
        "Use {game_name} for the game name and {steam_game_id} for the Steam game ID."
    ),
    "{game_name} ({steam_game_id}).7z",
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
                BACKUP_ARCHIVE_NAME_TEMPLATE_PROPERTY,
                BACKUP_ARCHIVE_COMMAND_PROPERTY,
                BACKUP_RESTORE_COMMAND_PROPERTY,
                BACKUP_RESTORE_IF_NOT_INSTALLED_PROPERTY,
            ],
            "Data Management",
            actions=[
                FeatureAction(
                    "backup-create-game",
                    "Backup Game Files",
                    "Backs up game files to the specified location.",
                    self.backup_game_files,
                ),
                FeatureAction(
                    "backup-restore-game",
                    "Restore Game Files",
                    "Restores game files from the backup location.",
                    self.restore_game_files,
                ),
            ],
        )

    def __get_backup_archive_name(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        backup_location = BACKUP_LOCATION_PROPERTY.get_or_fail(configuration)
        backup_name_template = BACKUP_ARCHIVE_NAME_TEMPLATE_PROPERTY.get_or_fail(
            configuration
        )
        # pylint: disable=line-too-long
        archive_name = backup_name_template.format(
            game_name=runtime_configuration.game_info.name,
            steam_game_id=runtime_configuration.get_game_identifier(),
        )
        return Path(f"{backup_location}/{archive_name}")

    def backup_game_files(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> None:
        """Backs up game files to a specified location.

        Args:
            configuration (dict[str, Any]): The configuration dictionary containing backup settings.
            runtime_configuration (RuntimeConfiguration): The runtime
            configuration, providing game paths and options.

        Returns:
            None
        """
        game_files_location = (
            runtime_configuration.steam_environment_data.steam_compat_install_path
        )
        archive_name = self.__get_backup_archive_name(
            configuration, runtime_configuration
        )
        command_template = BACKUP_ARCHIVE_COMMAND_PROPERTY.get(configuration)
        if not command_template:
            self.logger.error("Backup archive command template is not defined.")
            return

        if archive_name.exists():
            self.logger.info(
                "Backup archive %s already exists. Skipping backup.", archive_name
            )
            return

        command = command_template.format(
            archive=archive_name, source=game_files_location
        )
        if runtime_configuration.dry_run:
            self.logger.info(LOG_DRY_RUN.format("Backup command: %s"), command)
            return
        process = ProcessRunner.run_in_external_terminal(
            runtime_configuration.external_terminal_command_template,
            command,
            self.logger,
        )
        if process:
            with process:
                self.logger.info(
                    "Backing up game files from %s to %s...",
                    game_files_location,
                    archive_name,
                )
                _ = process.wait()
                self.logger.info(
                    "Game files backed up to %s successfully.", archive_name
                )

    def restore_game_files(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> None:
        """Restores game files from the backup location.

        Args:
            configuration (dict[str, Any]): The configuration dictionary
            containing restore settings.
            runtime_configuration (RuntimeConfiguration): The runtime
            configuration, providing game paths and options.

        Returns:
            None
        """
        if not runtime_configuration.steam_environment_data.steam_compat_install_path:
            self.logger.warning(
                "Steam compatibility install path is not set. Cannot restore game files."
            )
            return
        # Get the parent directory of the Steam compatibility install path
        game_files_location = Path(
            runtime_configuration.steam_environment_data.steam_compat_install_path
        ).parent
        archive_name = self.__get_backup_archive_name(
            configuration, runtime_configuration
        )
        command_template = BACKUP_RESTORE_COMMAND_PROPERTY.get(configuration)
        if not command_template:
            self.logger.error("Backup restore command template is not defined.")
            return

        if not archive_name.exists():
            self.logger.error(
                "Backup archive %s doesn't exists. Skipping restore.", archive_name
            )
            return

        command = command_template.format(
            archive=archive_name, destination=game_files_location
        )
        if runtime_configuration.dry_run:
            self.logger.info(LOG_DRY_RUN.format("Restore command: %s"), command)
            return
        process = ProcessRunner.run_in_external_terminal(
            runtime_configuration.external_terminal_command_template,
            command,
            self.logger,
        )
        if process:
            with process:
                self.logger.info(
                    "Restoring up game files from %s to %s...",
                    archive_name,
                    game_files_location,
                )
                _ = process.wait()
                self.logger.info(
                    "Game files restored up to %s successfully.", game_files_location
                )

    @override
    def before_execution(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        if (
            not runtime_configuration.game_executable_command
            or not runtime_configuration.game_executable_command.command
        ):
            self.logger.info(
                "Steam game executable not set. Skipping restoration check."
            )
            return

        game_executable = Path(runtime_configuration.game_executable_command.command)
        if (
            not game_executable.exists()
            and BACKUP_RESTORE_IF_NOT_INSTALLED_PROPERTY.get(configuration, False)
        ):
            self.logger.info(
                "Game executable '%s' not found. Initiating restoration from backup.",
                game_executable,
            )
            self.restore_game_files(configuration, runtime_configuration)
