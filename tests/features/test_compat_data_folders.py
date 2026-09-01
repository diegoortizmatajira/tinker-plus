import unittest
from unittest.mock import patch

from features.compat_data_folders import CompatDataFolders
from model import RuntimeConfiguration


class TestCompatDataFoldersDeleteCompatFolder(unittest.TestCase):
    def setUp(self):
        self.feature = CompatDataFolders()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False

        self.delete_patcher = patch(
            "features.compat_data_folders.FileSystem.delete_folder_tree"
        )
        self.mock_delete = self.delete_patcher.start()
        self.addCleanup(self.delete_patcher.stop)

    def test_deletes_when_compat_data_path_set(self):
        self.runtime_configuration.steam_environment_data.steam_compat_data_path = (
            "/compatdata/123"
        )
        self.feature.delete_compat_folder({}, self.runtime_configuration)
        self.mock_delete.assert_called_once()
        self.assertEqual(self.mock_delete.call_args[0][0], "/compatdata/123")
        self.assertFalse(self.mock_delete.call_args.kwargs["dry_run"])

    def test_skips_when_no_compat_data_path(self):
        self.feature.delete_compat_folder({}, self.runtime_configuration)
        self.mock_delete.assert_not_called()

    def test_forwards_dry_run_flag(self):
        self.runtime_configuration.steam_environment_data.steam_compat_data_path = (
            "/compatdata/123"
        )
        self.runtime_configuration.dry_run = True
        self.feature.delete_compat_folder({}, self.runtime_configuration)
        self.assertTrue(self.mock_delete.call_args.kwargs["dry_run"])


class TestCompatDataFoldersRecreateCompatFolder(unittest.TestCase):
    def setUp(self):
        self.feature = CompatDataFolders()
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_recreate_compat_folder_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.feature.recreate_compat_folder({}, self.runtime_configuration)


if __name__ == "__main__":
    _ = unittest.main()
