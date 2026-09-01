import logging
import unittest
from unittest.mock import patch

from core.wine import Wine
from model import RuntimeConfiguration

TEST_LOGGER = logging.getLogger("test")


class TestWine(unittest.TestCase):
    def test_get_windows_list_items_returns_all_known_versions(self):
        items = Wine.get_windows_list_items(RuntimeConfiguration.empty(), TEST_LOGGER)
        self.assertEqual(
            {item.name for item in items},
            {"winxp", "win7", "win8", "win10", "win11"},
        )

    @patch("core.wine.ProcessRunner.run_in_wine_prefix")
    def test_get_win_version_parses_matching_line(self, mock_run: unittest.mock.MagicMock):
        mock_run.return_value = (True, "win10 (Windows 10)\nother line\n")
        result = Wine.get_win_version(RuntimeConfiguration.empty(), TEST_LOGGER)
        self.assertEqual(result, "win10")
        # Regression test: Command(command_str, args_str) is NOT the same as
        # Command.from_parts(command_str, args_str) - the former misassigns args_str
        # to Command.cwd instead of building an argument list. get_full_command()
        # must therefore actually contain the "/v" flag as a real argument.
        command = mock_run.call_args[0][0]
        self.assertEqual(command.get_full_command(), "winecfg /v")

    @patch("core.wine.ProcessRunner.run_in_wine_prefix")
    def test_get_win_version_returns_none_when_command_fails(
        self, mock_run: unittest.mock.MagicMock
    ):
        mock_run.return_value = (False, "")
        result = Wine.get_win_version(RuntimeConfiguration.empty(), TEST_LOGGER)
        self.assertIsNone(result)

    @patch("core.wine.ProcessRunner.run_in_wine_prefix")
    def test_get_win_version_returns_none_when_no_line_matches(
        self, mock_run: unittest.mock.MagicMock
    ):
        mock_run.return_value = (True, "some unrelated output\n")
        result = Wine.get_win_version(RuntimeConfiguration.empty(), TEST_LOGGER)
        self.assertIsNone(result)

    def test_set_win_version_raises_for_unsupported_version(self):
        with self.assertRaises(ValueError):
            Wine.set_win_version(
                "win95", RuntimeConfiguration.empty(), TEST_LOGGER
            )

    @patch("core.wine.ProcessRunner.run_in_wine_prefix")
    def test_set_win_version_raises_when_command_fails(
        self, mock_run: unittest.mock.MagicMock
    ):
        mock_run.return_value = False
        with self.assertRaises(RuntimeError):
            Wine.set_win_version(
                "win10", RuntimeConfiguration.empty(), TEST_LOGGER
            )

    @patch("core.wine.ProcessRunner.run_in_wine_prefix")
    def test_set_win_version_succeeds_without_raising(
        self, mock_run: unittest.mock.MagicMock
    ):
        mock_run.return_value = True
        Wine.set_win_version("win10", RuntimeConfiguration.empty(), TEST_LOGGER)
        mock_run.assert_called_once()
        command = mock_run.call_args[0][0]
        self.assertEqual(command.get_full_command(), "winecfg /v win10")


if __name__ == "__main__":
    _ = unittest.main()
