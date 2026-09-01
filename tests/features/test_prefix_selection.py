import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from features.prefix_selection import PrefixSelection
from model import RuntimeConfiguration


class TestPrefixSelectionApplyConfiguration(unittest.TestCase):
    def setUp(self):
        self.feature = PrefixSelection()
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_uses_custom_prefix_when_configured(self):
        self.runtime_configuration.prefix_path = "/default/prefix"
        result = self.feature.apply_configuration(
            {"PREFIX_CUSTOM_PATH": "/custom/prefix"}, self.runtime_configuration
        )
        self.assertEqual(result.prefix_path, "/custom/prefix")

    def test_custom_prefix_overrides_even_when_no_default_set(self):
        self.runtime_configuration.prefix_path = None
        result = self.feature.apply_configuration(
            {"PREFIX_CUSTOM_PATH": "/custom/prefix"}, self.runtime_configuration
        )
        self.assertEqual(result.prefix_path, "/custom/prefix")

    def test_keeps_existing_prefix_when_no_custom_prefix_configured(self):
        self.runtime_configuration.prefix_path = "/default/prefix"
        result = self.feature.apply_configuration({}, self.runtime_configuration)
        self.assertEqual(result.prefix_path, "/default/prefix")

    def test_raises_when_neither_custom_nor_default_prefix_set(self):
        self.runtime_configuration.prefix_path = None
        with self.assertRaises(RuntimeError):
            self.feature.apply_configuration({}, self.runtime_configuration)


class TestPrefixSelectionExecuteInPipeline(unittest.TestCase):
    def setUp(self):
        self.feature = PrefixSelection()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False

        self.run_patcher = patch(
            "features.prefix_selection.ProcessRunner.run_command_with_compatibility_tool"
        )
        self.mock_run = self.run_patcher.start()
        self.addCleanup(self.run_patcher.stop)

    def test_forces_prefix_creation_when_directory_does_not_exist(self):
        self.runtime_configuration.prefix_path = "/nonexistent/prefix/path"
        self.feature.execute_in_pipeline({}, self.runtime_configuration)
        self.mock_run.assert_called_once()
        command = self.mock_run.call_args.args[0]
        self.assertEqual(command.command, "/bin/echo")
        self.assertIs(self.mock_run.call_args.args[1], self.runtime_configuration)

    def test_skips_when_prefix_directory_already_exists(self):
        with TemporaryDirectory() as tmp_dir:
            self.runtime_configuration.prefix_path = tmp_dir
            self.feature.execute_in_pipeline({}, self.runtime_configuration)
        self.mock_run.assert_not_called()

    def test_skips_when_prefix_path_is_none_because_cwd_exists(self):
        self.runtime_configuration.prefix_path = None
        self.feature.execute_in_pipeline({}, self.runtime_configuration)
        self.mock_run.assert_not_called()


if __name__ == "__main__":
    _ = unittest.main()
