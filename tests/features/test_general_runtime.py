import unittest
from unittest.mock import MagicMock, patch

from features.general_runtime import GeneralRuntime
from model import GameInfo, RuntimeConfiguration, SteamEnvironmentData


class TestGeneralRuntimeBuildConfiguration(unittest.TestCase):
    def setUp(self):
        self.feature = GeneralRuntime()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.original_command = ["steam-launch-wrapper", "game.exe"]

        self.parse_patcher = patch("features.general_runtime.SteamParser.parse")
        self.mock_parse = self.parse_patcher.start()
        self.addCleanup(self.parse_patcher.stop)

        self.save_patcher = patch("features.general_runtime.SteamParser.save")
        self.mock_save = self.save_patcher.start()
        self.addCleanup(self.save_patcher.stop)

        self.get_game_info_patcher = patch(
            "features.general_runtime.SteamUtil.get_game_info"
        )
        self.mock_get_game_info = self.get_game_info_patcher.start()
        self.mock_get_game_info.return_value = GameInfo("123", "Test Game")
        self.addCleanup(self.get_game_info_patcher.stop)

        self.from_cache_patcher = patch(
            "features.general_runtime.CompatToolInfoRepository.from_cache"
        )
        self.mock_from_cache = self.from_cache_patcher.start()
        self.mock_from_cache.return_value = None
        self.addCleanup(self.from_cache_patcher.stop)

        self.put_in_cache_patcher = patch(
            "features.general_runtime.CompatToolInfoRepository.put_in_cache"
        )
        self.mock_put_in_cache = self.put_in_cache_patcher.start()
        self.addCleanup(self.put_in_cache_patcher.stop)

        self.scan_patcher = patch(
            "features.general_runtime.CompatToolInfoRepository.scan_and_populate_cache"
        )
        self.mock_scan = self.scan_patcher.start()
        self.addCleanup(self.scan_patcher.stop)

    def _set_parsed_data(self, **overrides):
        def fake_parse(data: SteamEnvironmentData, _full_command: str, _logger):
            for key, value in overrides.items():
                setattr(data, key, value)

        self.mock_parse.side_effect = fake_parse

    def test_parses_the_joined_original_command(self):
        self._set_parsed_data()
        self.feature.build_configuration({}, self.runtime_configuration)
        called_command = self.mock_parse.call_args[0][1]
        self.assertEqual(called_command, "steam-launch-wrapper game.exe")

    def test_saves_environment_data_only_when_valid(self):
        self._set_parsed_data(steam_game_id="123")
        self.feature.build_configuration({}, self.runtime_configuration)
        self.mock_save.assert_called_once()

    def test_does_not_save_environment_data_when_invalid(self):
        self._set_parsed_data()  # no steam_app_id/steam_game_id set
        self.feature.build_configuration({}, self.runtime_configuration)
        self.mock_save.assert_not_called()

    def test_save_forwards_dry_run_flag(self):
        self._set_parsed_data(steam_game_id="123")
        self.runtime_configuration.dry_run = True
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertTrue(self.mock_save.call_args[0][1])

    def test_creates_and_caches_compat_tool_info_when_not_cached(self):
        self._set_parsed_data(
            cmd_steam_compatibility_tool="GE-Proton10-25",
            cmd_steam_compatibility_tools_path="/tools",
        )
        self.mock_from_cache.return_value = None
        self.feature.build_configuration({}, self.runtime_configuration)
        self.mock_put_in_cache.assert_called_once()
        cached_item = self.mock_put_in_cache.call_args[0][0]
        self.assertEqual(cached_item.name, "GE-Proton10-25")
        self.assertEqual(cached_item.dir, "/tools")

    def test_skips_put_in_cache_when_already_cached(self):
        self._set_parsed_data(cmd_steam_compatibility_tool="GE-Proton10-25")
        self.mock_from_cache.return_value = MagicMock()
        self.feature.build_configuration({}, self.runtime_configuration)
        self.mock_put_in_cache.assert_not_called()

    def test_from_cache_and_put_in_cache_forward_dry_run(self):
        self._set_parsed_data(cmd_steam_compatibility_tool="GE-Proton10-25")
        self.runtime_configuration.dry_run = True
        self.mock_from_cache.return_value = None
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertTrue(self.mock_from_cache.call_args[0][2])
        self.assertTrue(self.mock_put_in_cache.call_args[0][2])

    def test_scan_and_populate_cache_forwards_dry_run(self):
        self._set_parsed_data()
        self.runtime_configuration.dry_run = True
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertTrue(self.mock_scan.call_args[0][2])

    def test_sets_prefix_path_from_compat_data_path(self):
        self._set_parsed_data(steam_compat_data_path="/compatdata/123")
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertEqual(self.runtime_configuration.prefix_path, "/compatdata/123/pfx")

    def test_builds_game_executable_command_from_parsed_exe(self):
        self._set_parsed_data(
            cmd_steam_game_exe="/games/foo/foo.exe",
            cmd_steam_game_args="--windowed",
            steam_compat_install_path="/games/foo",
        )
        self.feature.build_configuration({}, self.runtime_configuration)
        command = self.runtime_configuration.game_executable_command
        assert command is not None
        self.assertEqual(command.command, "/games/foo/foo.exe")
        self.assertEqual(command.get_full_command(), "/games/foo/foo.exe --windowed")
        self.assertEqual(command.cwd, "/games/foo")

    def test_falls_back_to_echo_when_no_exe_parsed(self):
        self._set_parsed_data()
        self.feature.build_configuration({}, self.runtime_configuration)
        command = self.runtime_configuration.game_executable_command
        assert command is not None
        self.assertEqual(command.command, "echo")

    def test_sets_game_info_from_steam_util(self):
        self._set_parsed_data()
        self.feature.build_configuration({}, self.runtime_configuration)
        self.assertEqual(self.runtime_configuration.game_info.name, "Test Game")


class TestGeneralRuntimeApplyConfiguration(unittest.TestCase):
    def test_sets_log_executable_commands_flag(self):
        feature = GeneralRuntime()
        runtime_configuration = RuntimeConfiguration.empty()
        feature.apply_configuration(
            {"GENERAL_LOG_INDIVIDUAL_EXE": True}, runtime_configuration
        )
        self.assertTrue(runtime_configuration.log_executable_commands)

    def test_defaults_log_executable_commands_to_false(self):
        feature = GeneralRuntime()
        runtime_configuration = RuntimeConfiguration.empty()
        feature.apply_configuration({}, runtime_configuration)
        self.assertFalse(runtime_configuration.log_executable_commands)


if __name__ == "__main__":
    _ = unittest.main()
