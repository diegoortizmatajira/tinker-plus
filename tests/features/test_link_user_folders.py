import unittest
from unittest.mock import MagicMock, patch

from features.link_user_folders import LinkUserFolders
from model import RuntimeConfiguration


class TestLinkUserFolders(unittest.TestCase):
    def setUp(self):
        self.feature = LinkUserFolders()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False
        self.runtime_configuration.prefix_path = "/prefix"

        self.link_patcher = patch(
            "features.link_user_folders.FileSystem.create_symbolic_link"
        )
        self.mock_link = self.link_patcher.start()
        self.addCleanup(self.link_patcher.stop)

    def _call_args_by_source(self) -> dict[str, unittest.mock._Call]:
        return {call.args[0]: call for call in self.mock_link.call_args_list}

    def test_skips_entirely_when_no_prefix_path(self):
        self.runtime_configuration.prefix_path = None
        with self.assertLogs(level="WARNING"):
            self.feature.before_execution({}, self.runtime_configuration)
        self.mock_link.assert_not_called()

    def test_links_steam_user_folder_when_configured(self):
        self.feature.before_execution(
            {"LINK_STEAM_USER_FOLDER": "/home/user/steam"}, self.runtime_configuration
        )
        calls = self._call_args_by_source()
        self.assertIn("/home/user/steam", calls)
        self.assertTrue(calls["/home/user/steam"].args[1].endswith("/steamuser"))

    def test_links_public_user_folder_when_configured(self):
        self.feature.before_execution(
            {"LINK_PUBLIC_USER_FOLDER": "/home/user/public"}, self.runtime_configuration
        )
        calls = self._call_args_by_source()
        self.assertIn("/home/user/public", calls)
        self.assertTrue(calls["/home/user/public"].args[1].endswith("/Public"))

    def test_links_custom_folder_when_both_source_and_destination_set(self):
        self.feature.before_execution(
            {
                "LINK_CUSTOM_SOURCE": "/data/saves",
                "LINK_CUSTOM_DESTINATION": "MyGame/Saves",
            },
            self.runtime_configuration,
        )
        calls = self._call_args_by_source()
        self.assertIn("/data/saves", calls)
        self.assertTrue(calls["/data/saves"].args[1].endswith("MyGame/Saves"))

    def test_skips_custom_folder_when_only_source_set(self):
        self.feature.before_execution(
            {"LINK_CUSTOM_SOURCE": "/data/saves"}, self.runtime_configuration
        )
        self.mock_link.assert_not_called()

    def test_should_backup_defaults_true_and_applies_to_all_three_link_types(self):
        self.feature.before_execution(
            {
                "LINK_STEAM_USER_FOLDER": "/steam",
                "LINK_PUBLIC_USER_FOLDER": "/public",
                "LINK_CUSTOM_SOURCE": "/custom",
                "LINK_CUSTOM_DESTINATION": "dest",
            },
            self.runtime_configuration,
        )
        self.assertEqual(self.mock_link.call_count, 3)
        for call in self.mock_link.call_args_list:
            self.assertTrue(call.kwargs["should_backup"])

    def test_should_backup_false_applies_to_all_three_link_types(self):
        # Regression test: previously only the Steam user folder respected an
        # explicit LINK_SHOULD_BACKUP_FOLDERS=False; public/custom always backed up.
        self.feature.before_execution(
            {
                "LINK_STEAM_USER_FOLDER": "/steam",
                "LINK_PUBLIC_USER_FOLDER": "/public",
                "LINK_CUSTOM_SOURCE": "/custom",
                "LINK_CUSTOM_DESTINATION": "dest",
                "LINK_SHOULD_BACKUP_FOLDERS": False,
            },
            self.runtime_configuration,
        )
        self.assertEqual(self.mock_link.call_count, 3)
        for call in self.mock_link.call_args_list:
            self.assertFalse(call.kwargs["should_backup"])

    def test_dry_run_does_not_call_create_symbolic_link(self):
        self.runtime_configuration.dry_run = True
        self.feature.before_execution(
            {"LINK_STEAM_USER_FOLDER": "/steam"}, self.runtime_configuration
        )
        self.mock_link.assert_not_called()

    def test_dry_run_still_logs_intended_link(self):
        self.runtime_configuration.dry_run = True
        with self.assertLogs(level="INFO") as captured:
            self.feature.before_execution(
                {"LINK_STEAM_USER_FOLDER": "/steam"}, self.runtime_configuration
            )
        self.assertTrue(
            any("Ensure user folder link" in message for message in captured.output)
        )


if __name__ == "__main__":
    _ = unittest.main()
