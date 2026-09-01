import unittest
from unittest.mock import MagicMock, patch

from features.human_readable_links import HumanReadableLinks
from model import Command, RuntimeConfiguration


class TestHumanReadableLinks(unittest.TestCase):
    def setUp(self):
        self.feature = HumanReadableLinks()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False
        self.runtime_configuration.game_info.name = "Hollow Knight"
        self.runtime_configuration.game_executable_command = Command.from_string(
            "hollow_knight.exe"
        )

        self.makedirs_patcher = patch("features.human_readable_links.os.makedirs")
        self.mock_makedirs = self.makedirs_patcher.start()
        self.addCleanup(self.makedirs_patcher.stop)

        self.link_patcher = patch(
            "features.human_readable_links.FileSystem.create_symbolic_link"
        )
        self.mock_link = self.link_patcher.start()
        self.addCleanup(self.link_patcher.stop)

        self.log_factory_patcher = patch("features.human_readable_links.LogFactory")
        mock_log_factory_class = self.log_factory_patcher.start()
        mock_log_factory_class.singleton.return_value.get_log_filename.return_value = (
            "/logs/lastrun.log"
        )
        self.addCleanup(self.log_factory_patcher.stop)

    def test_skips_when_no_game_executable_command(self):
        self.runtime_configuration.game_executable_command = None
        self.feature.before_execution({}, self.runtime_configuration)
        self.mock_makedirs.assert_not_called()

    def test_skips_when_game_executable_command_is_empty(self):
        self.runtime_configuration.game_executable_command = MagicMock(command="")
        self.feature.before_execution({}, self.runtime_configuration)
        self.mock_makedirs.assert_not_called()

    def test_dry_run_does_not_create_directory_or_links(self):
        self.runtime_configuration.dry_run = True
        self.feature.before_execution({}, self.runtime_configuration)
        self.mock_makedirs.assert_not_called()
        self.mock_link.assert_not_called()

    def test_creates_links_for_config_environment_and_logs(self):
        self.feature.before_execution({}, self.runtime_configuration)
        self.mock_makedirs.assert_called_once()
        # config.json, environment.json, logs, and the last-run log are always linked.
        linked_targets = [call.args[1] for call in self.mock_link.call_args_list]
        self.assertTrue(any(t.endswith("/config.json") for t in linked_targets))
        self.assertTrue(any(t.endswith("/environment.json") for t in linked_targets))
        self.assertTrue(any(t.endswith("/logs") for t in linked_targets))

    def test_links_game_files_only_when_path_available(self):
        self.runtime_configuration.steam_environment_data.steam_compat_install_path = (
            "/games/hollow_knight"
        )
        self.feature.before_execution({}, self.runtime_configuration)
        linked_targets = [call.args[1] for call in self.mock_link.call_args_list]
        self.assertTrue(any(t.endswith("/game_files") for t in linked_targets))

    def test_skips_game_files_link_when_path_unavailable(self):
        self.feature.before_execution({}, self.runtime_configuration)
        linked_targets = [call.args[1] for call in self.mock_link.call_args_list]
        self.assertFalse(any(t.endswith("/game_files") for t in linked_targets))

    def test_links_compat_data_only_when_path_available(self):
        self.runtime_configuration.steam_environment_data.steam_compat_data_path = (
            "/compatdata/123"
        )
        self.feature.before_execution({}, self.runtime_configuration)
        linked_targets = [call.args[1] for call in self.mock_link.call_args_list]
        self.assertTrue(any(t.endswith("/compat_data") for t in linked_targets))

    def test_oserror_from_makedirs_is_caught_and_logged(self):
        self.mock_makedirs.side_effect = OSError("permission denied")
        with self.assertLogs(level="WARNING"):
            self.feature.before_execution({}, self.runtime_configuration)
        # Should not propagate and abort the pipeline.

    def test_runtimeerror_from_create_symbolic_link_is_caught_and_logged(self):
        self.mock_link.side_effect = RuntimeError("link failed")
        with self.assertLogs(level="WARNING"):
            self.feature.before_execution({}, self.runtime_configuration)


if __name__ == "__main__":
    _ = unittest.main()
