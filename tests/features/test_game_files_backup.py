import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from features.game_files_backup import GameFilesBackup
from model import Command, RuntimeConfiguration


class TestGameFilesBackupArchiveName(unittest.TestCase):
    def setUp(self):
        self.feature = GameFilesBackup()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.game_info.name = "Hollow Knight"
        self.runtime_configuration.steam_environment_data.steam_game_id = "123"

    def test_builds_archive_path_from_location_and_default_template(self):
        archive = self.feature._get_backup_archive_name(
            {"BACKUP_LOCATION": "/backups"}, self.runtime_configuration
        )
        self.assertEqual(archive, Path("/backups/Hollow Knight (123).7z"))

    def test_uses_custom_template_when_provided(self):
        archive = self.feature._get_backup_archive_name(
            {
                "BACKUP_LOCATION": "/backups",
                "BACKUP_ARCHIVE_NAME_TEMPLATE": "{game_name}-{steam_game_id}.zip",
            },
            self.runtime_configuration,
        )
        self.assertEqual(archive, Path("/backups/Hollow Knight-123.zip"))

    def test_raises_when_backup_location_missing(self):
        with self.assertRaises(KeyError):
            _ = self.feature._get_backup_archive_name({}, self.runtime_configuration)


class TestGameFilesBackupBackupGameFiles(unittest.TestCase):
    def setUp(self):
        self.feature = GameFilesBackup()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False
        self.runtime_configuration.game_info.name = "Hollow Knight"
        self.runtime_configuration.steam_environment_data.steam_game_id = "123"
        self.runtime_configuration.steam_environment_data.steam_compat_install_path = (
            "/games/hollow_knight"
        )
        self.runtime_configuration.external_terminal_command_template = [
            "xterm",
            "-e",
            "{command}",
        ]

        self.tmp_dir = TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        self.config = {"BACKUP_LOCATION": self.tmp_dir.name}

        self.run_terminal_patcher = patch(
            "features.game_files_backup.ProcessRunner.run_in_external_terminal"
        )
        self.mock_run_terminal = self.run_terminal_patcher.start()
        self.addCleanup(self.run_terminal_patcher.stop)
        self.mock_process = MagicMock()
        self.mock_process.wait.return_value = 0
        self.mock_run_terminal.return_value = self.mock_process

    def _archive_path(self) -> Path:
        return self.feature._get_backup_archive_name(
            self.config, self.runtime_configuration
        )

    def test_skips_backup_when_no_command_template_configured(self):
        self.config["BACKUP_ARCHIVE_COMMAND"] = ""
        with self.assertLogs(level="ERROR"):
            self.feature.backup_game_files(self.config, self.runtime_configuration)
        self.mock_run_terminal.assert_not_called()

    def test_skips_backup_when_archive_already_exists(self):
        self._archive_path().touch()
        with self.assertLogs(level="INFO"):
            self.feature.backup_game_files(self.config, self.runtime_configuration)
        self.mock_run_terminal.assert_not_called()

    def test_dry_run_logs_instead_of_running_terminal_command(self):
        self.runtime_configuration.dry_run = True
        with self.assertLogs(level="INFO") as captured:
            self.feature.backup_game_files(self.config, self.runtime_configuration)
        self.mock_run_terminal.assert_not_called()
        self.assertTrue(any("DRY RUN" in message for message in captured.output))

    def test_runs_backup_command_in_external_terminal(self):
        self.feature.backup_game_files(self.config, self.runtime_configuration)
        self.mock_run_terminal.assert_called_once()
        call_args = self.mock_run_terminal.call_args
        self.assertEqual(
            call_args.args[0],
            self.runtime_configuration.external_terminal_command_template,
        )
        self.assertIn(str(self._archive_path()), call_args.args[1])
        self.assertIn("/games/hollow_knight", call_args.args[1])
        self.mock_process.wait.assert_called_once()


class TestGameFilesBackupRestoreGameFiles(unittest.TestCase):
    def setUp(self):
        self.feature = GameFilesBackup()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False
        self.runtime_configuration.game_info.name = "Hollow Knight"
        self.runtime_configuration.steam_environment_data.steam_game_id = "123"
        self.runtime_configuration.steam_environment_data.steam_compat_install_path = (
            "/games/hollow_knight/current"
        )
        self.runtime_configuration.external_terminal_command_template = [
            "xterm",
            "-e",
            "{command}",
        ]

        self.tmp_dir = TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        self.config = {"BACKUP_LOCATION": self.tmp_dir.name}

        self.run_terminal_patcher = patch(
            "features.game_files_backup.ProcessRunner.run_in_external_terminal"
        )
        self.mock_run_terminal = self.run_terminal_patcher.start()
        self.addCleanup(self.run_terminal_patcher.stop)
        self.mock_process = MagicMock()
        self.mock_process.wait.return_value = 0
        self.mock_run_terminal.return_value = self.mock_process

    def _archive_path(self) -> Path:
        return self.feature._get_backup_archive_name(
            self.config, self.runtime_configuration
        )

    def test_skips_restore_when_no_compat_install_path(self):
        self.runtime_configuration.steam_environment_data.steam_compat_install_path = (
            None
        )
        with self.assertLogs(level="WARNING"):
            self.feature.restore_game_files(self.config, self.runtime_configuration)
        self.mock_run_terminal.assert_not_called()

    def test_skips_restore_when_no_command_template_configured(self):
        self.config["BACKUP_RESTORE_COMMAND"] = ""
        with self.assertLogs(level="ERROR"):
            self.feature.restore_game_files(self.config, self.runtime_configuration)
        self.mock_run_terminal.assert_not_called()

    def test_skips_restore_when_archive_does_not_exist(self):
        with self.assertLogs(level="ERROR"):
            self.feature.restore_game_files(self.config, self.runtime_configuration)
        self.mock_run_terminal.assert_not_called()

    def test_dry_run_logs_instead_of_running_terminal_command(self):
        self._archive_path().touch()
        self.runtime_configuration.dry_run = True
        with self.assertLogs(level="INFO") as captured:
            self.feature.restore_game_files(self.config, self.runtime_configuration)
        self.mock_run_terminal.assert_not_called()
        self.assertTrue(any("DRY RUN" in message for message in captured.output))

    def test_runs_restore_command_in_external_terminal(self):
        archive = self._archive_path()
        archive.touch()
        self.feature.restore_game_files(self.config, self.runtime_configuration)
        self.mock_run_terminal.assert_called_once()
        call_args = self.mock_run_terminal.call_args
        self.assertIn(str(archive), call_args.args[1])
        self.assertIn("/games/hollow_knight", call_args.args[1])
        self.mock_process.wait.assert_called_once()


class TestGameFilesBackupBeforeExecution(unittest.TestCase):
    def setUp(self):
        self.feature = GameFilesBackup()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False

        self.restore_patcher = patch.object(self.feature, "restore_game_files")
        self.mock_restore = self.restore_patcher.start()
        self.addCleanup(self.restore_patcher.stop)

        self.tmp_dir = TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)

    def test_skips_when_no_game_executable_command(self):
        self.runtime_configuration.game_executable_command = None
        self.feature.before_execution({}, self.runtime_configuration)
        self.mock_restore.assert_not_called()

    def test_skips_when_game_executable_command_is_empty(self):
        self.runtime_configuration.game_executable_command = MagicMock(command="")
        self.feature.before_execution({}, self.runtime_configuration)
        self.mock_restore.assert_not_called()

    def test_skips_restore_when_executable_exists(self):
        existing_exe = Path(self.tmp_dir.name) / "game.exe"
        existing_exe.touch()
        self.runtime_configuration.game_executable_command = Command.from_string(
            str(existing_exe)
        )
        self.feature.before_execution(
            {"BACKUP_RESTORE_IF_NOT_INSTALLED": True}, self.runtime_configuration
        )
        self.mock_restore.assert_not_called()

    def test_skips_restore_when_missing_but_flag_disabled(self):
        missing_exe = Path(self.tmp_dir.name) / "missing.exe"
        self.runtime_configuration.game_executable_command = Command.from_string(
            str(missing_exe)
        )
        self.feature.before_execution(
            {"BACKUP_RESTORE_IF_NOT_INSTALLED": False}, self.runtime_configuration
        )
        self.mock_restore.assert_not_called()

    def test_skips_restore_when_missing_and_flag_defaults_to_disabled(self):
        missing_exe = Path(self.tmp_dir.name) / "missing.exe"
        self.runtime_configuration.game_executable_command = Command.from_string(
            str(missing_exe)
        )
        self.feature.before_execution({}, self.runtime_configuration)
        self.mock_restore.assert_not_called()

    def test_restores_when_missing_and_flag_enabled(self):
        missing_exe = Path(self.tmp_dir.name) / "missing.exe"
        self.runtime_configuration.game_executable_command = Command.from_string(
            str(missing_exe)
        )
        configuration = {"BACKUP_RESTORE_IF_NOT_INSTALLED": True}
        self.feature.before_execution(configuration, self.runtime_configuration)
        self.mock_restore.assert_called_once_with(
            configuration, self.runtime_configuration
        )


if __name__ == "__main__":
    _ = unittest.main()
