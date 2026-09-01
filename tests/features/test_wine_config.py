import unittest
from unittest.mock import patch

from features.wine_config import WineConfig
from model import RuntimeConfiguration


class TestWineConfigBeforeExecution(unittest.TestCase):
    def setUp(self):
        self.feature = WineConfig()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False

        self.get_win_version_patcher = patch(
            "features.wine_config.Wine.get_win_version"
        )
        self.mock_get_win_version = self.get_win_version_patcher.start()
        self.addCleanup(self.get_win_version_patcher.stop)

        self.set_win_version_patcher = patch(
            "features.wine_config.Wine.set_win_version"
        )
        self.mock_set_win_version = self.set_win_version_patcher.start()
        self.addCleanup(self.set_win_version_patcher.stop)

    def test_does_nothing_when_no_windows_version_configured(self):
        self.feature.before_execution({}, self.runtime_configuration)
        self.mock_get_win_version.assert_not_called()
        self.mock_set_win_version.assert_not_called()

    def test_skips_set_when_current_version_already_matches(self):
        self.mock_get_win_version.return_value = "win10"
        self.feature.before_execution(
            {"WINE_WINDOWS_VERSION": "win10"}, self.runtime_configuration
        )
        self.mock_set_win_version.assert_not_called()

    def test_sets_version_when_it_differs_from_current(self):
        self.mock_get_win_version.return_value = "win7"
        self.feature.before_execution(
            {"WINE_WINDOWS_VERSION": "win10"}, self.runtime_configuration
        )
        self.mock_set_win_version.assert_called_once_with(
            "win10", self.runtime_configuration, self.feature.logger
        )

    def test_sets_version_when_current_version_unknown(self):
        self.mock_get_win_version.return_value = None
        self.feature.before_execution(
            {"WINE_WINDOWS_VERSION": "win11"}, self.runtime_configuration
        )
        self.mock_set_win_version.assert_called_once_with(
            "win11", self.runtime_configuration, self.feature.logger
        )


class TestWineConfigActions(unittest.TestCase):
    def setUp(self):
        self.feature = WineConfig()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False
        self.runtime_configuration.prefix_path = "/prefix"

        self.run_patcher = patch(
            "features.wine_config.ProcessRunner.run_in_wine_prefix"
        )
        self.mock_run = self.run_patcher.start()
        self.addCleanup(self.run_patcher.stop)

    def _action(self, alias: str):
        matches = [action for action in self.feature.actions if action.alias == alias]
        self.assertEqual(len(matches), 1, f"Expected exactly one action '{alias}'")
        return matches[0]

    def test_winetricks_action_runs_command_and_succeeds_silently(self):
        self.mock_run.return_value = True
        action = self._action("run-winetrics")
        action.action({}, self.runtime_configuration)
        self.mock_run.assert_called_once()
        command = self.mock_run.call_args.args[0]
        self.assertEqual(command.command, "winetricks")

    def test_winetricks_action_logs_error_but_does_not_raise_when_failed(self):
        self.mock_run.return_value = False
        action = self._action("run-winetrics")
        with self.assertLogs(level="ERROR"):
            action.action({}, self.runtime_configuration)

    def test_winetricks_action_raises_runtimeerror_on_failure(self):
        self.mock_run.side_effect = RuntimeError("boom")
        action = self._action("run-winetrics")
        with self.assertRaises(RuntimeError):
            action.action({}, self.runtime_configuration)

    def test_winecfg_action_runs_winecfg_with_no_args(self):
        self.mock_run.return_value = True
        action = self._action("run-winecfg")
        action.action({}, self.runtime_configuration)
        command = self.mock_run.call_args.args[0]
        self.assertEqual(command.get_full_command(), "winecfg")

    def test_uninstaller_action_runs_wine_with_uninstaller_arg(self):
        self.mock_run.return_value = True
        action = self._action("run-uninstaller")
        action.action({}, self.runtime_configuration)
        command = self.mock_run.call_args.args[0]
        self.assertEqual(command.command, "wine")
        self.assertEqual(command.get_full_command(), "wine uninstaller")


if __name__ == "__main__":
    _ = unittest.main()
