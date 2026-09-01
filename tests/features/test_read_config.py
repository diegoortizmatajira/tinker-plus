import unittest
from unittest.mock import MagicMock

from core import ConfigStorage
from features.read_config import ReadConfig
from model import GameInfo, RuntimeConfiguration


class TestReadConfigBuildConfiguration(unittest.TestCase):
    def setUp(self):
        self.mock_config_storage = MagicMock(spec=ConfigStorage)
        self.feature = ReadConfig(self.mock_config_storage)
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False
        self.runtime_configuration.game_info = GameInfo("123", "Hollow Knight")

        self.global_config_result = {"GLOBAL_KEY": "value"}
        self.game_config_result = {"GAME_KEY": "value"}
        self.mock_config_storage.build_global_configuration.return_value = (
            self.global_config_result
        )
        self.mock_config_storage.build_game_configuration.return_value = (
            self.game_config_result
        )

    def test_calls_build_global_configuration_before_build_game_configuration(self):
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertEqual(
            [call_item[0] for call_item in self.mock_config_storage.mock_calls],
            ["build_global_configuration", "build_game_configuration"],
        )

    def test_passes_sourced_configuration_to_build_global_configuration(self):
        sourced_configuration = {"KEY": "value"}
        self.feature.build_configuration(sourced_configuration, self.runtime_configuration)
        called_configuration = (
            self.mock_config_storage.build_global_configuration.call_args[0][0]
        )
        self.assertEqual(called_configuration, {"KEY": "value"})

    def test_forwards_dry_run_flag_to_build_global_configuration(self):
        self.runtime_configuration.dry_run = True
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertTrue(
            self.mock_config_storage.build_global_configuration.call_args.kwargs[
                "dry_run"
            ]
        )

    def test_build_global_configuration_dry_run_defaults_to_false(self):
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertFalse(
            self.mock_config_storage.build_global_configuration.call_args.kwargs[
                "dry_run"
            ]
        )

    def test_stores_loaded_global_configuration_snapshot_on_runtime_configuration(self):
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertEqual(
            self.runtime_configuration.loaded_global_configuration,
            self.global_config_result,
        )

    def test_loaded_global_configuration_is_a_copy_not_the_same_object(self):
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertIsNot(
            self.runtime_configuration.loaded_global_configuration,
            self.global_config_result,
        )

    def test_passes_game_info_to_build_game_configuration(self):
        self.feature.build_configuration({}, self.runtime_configuration)
        args = self.mock_config_storage.build_game_configuration.call_args[0]
        self.assertEqual(args[0], self.runtime_configuration.game_info)

    def test_passes_global_configuration_result_as_sourced_configuration_to_build_game_configuration(
        self,
    ):
        self.feature.build_configuration({}, self.runtime_configuration)
        args = self.mock_config_storage.build_game_configuration.call_args[0]
        self.assertEqual(args[1], self.global_config_result)

    def test_passes_loaded_global_configuration_snapshot_to_build_game_configuration(self):
        self.feature.build_configuration({}, self.runtime_configuration)
        args = self.mock_config_storage.build_game_configuration.call_args[0]
        self.assertEqual(args[2], self.runtime_configuration.loaded_global_configuration)

    def test_forwards_dry_run_flag_to_build_game_configuration(self):
        self.runtime_configuration.dry_run = True
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertTrue(
            self.mock_config_storage.build_game_configuration.call_args.kwargs[
                "dry_run"
            ]
        )

    def test_returns_result_of_build_game_configuration(self):
        result = self.feature.build_configuration({}, self.runtime_configuration)
        self.assertEqual(result, self.game_config_result)


if __name__ == "__main__":
    _ = unittest.main()
