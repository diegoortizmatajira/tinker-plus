import unittest
from unittest.mock import patch

from features.winetricks_install import WinetricksInstall
from model import RuntimeConfiguration


class TestWinetricksInstallBeforeExecution(unittest.TestCase):
    def setUp(self):
        self.feature = WinetricksInstall()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False
        self.runtime_configuration.prefix_path = "/prefix"

        self.run_patcher = patch(
            "features.winetricks_install.ProcessRunner.run_in_wine_prefix"
        )
        self.mock_run = self.run_patcher.start()
        self.addCleanup(self.run_patcher.stop)

    def test_does_nothing_when_winetricks_run_disabled(self):
        self.feature.before_execution(
            {"WINETRICKS_RUN": False, "WINETRICKS": ["dotnet48"]},
            self.runtime_configuration,
        )
        self.mock_run.assert_not_called()

    def test_runs_configured_packages_when_enabled(self):
        self.mock_run.return_value = True
        self.feature.before_execution(
            {"WINETRICKS_RUN": True, "WINETRICKS": ["dotnet48", "vcrun2019"]},
            self.runtime_configuration,
        )
        self.mock_run.assert_called_once()
        command = self.mock_run.call_args.args[0]
        self.assertEqual(command.command, "winetricks")
        self.assertEqual(
            command.get_full_command(), "winetricks --unattended dotnet48 vcrun2019"
        )

    def test_runs_by_default_when_winetricks_run_not_specified(self):
        # WINETRICKS_RUN defaults to True.
        self.mock_run.return_value = True
        self.feature.before_execution(
            {"WINETRICKS": ["dotnet48"]}, self.runtime_configuration
        )
        self.mock_run.assert_called_once()

    def test_skips_when_no_packages_configured(self):
        self.feature.before_execution(
            {"WINETRICKS_RUN": True, "WINETRICKS": []}, self.runtime_configuration
        )
        self.mock_run.assert_not_called()

    def test_skips_when_packages_is_list_with_single_empty_string(self):
        self.feature.before_execution(
            {"WINETRICKS_RUN": True, "WINETRICKS": [""]}, self.runtime_configuration
        )
        self.mock_run.assert_not_called()

    def test_raises_runtimeerror_when_installation_fails(self):
        self.mock_run.return_value = False
        with self.assertRaises(RuntimeError):
            self.feature.before_execution(
                {"WINETRICKS_RUN": True, "WINETRICKS": ["dotnet48"]},
                self.runtime_configuration,
            )

    def test_propagates_runtimeerror_raised_by_process_runner(self):
        self.mock_run.side_effect = RuntimeError("boom")
        with self.assertRaises(RuntimeError):
            self.feature.before_execution(
                {"WINETRICKS_RUN": True, "WINETRICKS": ["dotnet48"]},
                self.runtime_configuration,
            )


if __name__ == "__main__":
    _ = unittest.main()
