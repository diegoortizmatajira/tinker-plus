import unittest

from features.steam_tools import SteamTools
from model import Command, CommandCategory, RuntimeConfiguration


class TestSteamToolsDefaultCommands(unittest.TestCase):
    def setUp(self):
        self.feature = SteamTools()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.steam_environment_data.steam_base_folder = (
            "/steamapps/common/Steam Linux Runtime"
        )
        # Disable all pipeline wrappers by default so these tests focus purely
        # on the default-command restoration behavior.
        self.base_configuration = {
            "STEAM_USE_WRAPPER": False,
            "STEAM_USE_REAPER": False,
            "STEAM_USE_SNIPER": False,
        }

    def test_restores_default_wrapper_command_when_missing(self):
        self.feature.apply_configuration(self.base_configuration, self.runtime_configuration)
        self.assertEqual(
            self.runtime_configuration.steam_environment_data.cmd_steam_wrapper,
            "/steamapps/common/Steam Linux Runtime/ubuntu12_32/steam-launch-wrapper",
        )

    def test_does_not_override_existing_wrapper_command(self):
        self.runtime_configuration.steam_environment_data.cmd_steam_wrapper = (
            "/custom/wrapper"
        )
        self.feature.apply_configuration(self.base_configuration, self.runtime_configuration)
        self.assertEqual(
            self.runtime_configuration.steam_environment_data.cmd_steam_wrapper,
            "/custom/wrapper",
        )

    def test_restores_default_sniper_command_when_missing(self):
        self.feature.apply_configuration(self.base_configuration, self.runtime_configuration)
        self.assertEqual(
            self.runtime_configuration.steam_environment_data.cmd_steam_sniper,
            "/steamapps/common/Steam Linux Runtime/steamapps/common/"
            "SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun",
        )

    def test_does_not_override_existing_sniper_command(self):
        self.runtime_configuration.steam_environment_data.cmd_steam_sniper = (
            "/custom/sniper"
        )
        self.feature.apply_configuration(self.base_configuration, self.runtime_configuration)
        self.assertEqual(
            self.runtime_configuration.steam_environment_data.cmd_steam_sniper,
            "/custom/sniper",
        )

    def test_restores_default_reaper_command_when_missing(self):
        self.feature.apply_configuration(self.base_configuration, self.runtime_configuration)
        self.assertEqual(
            self.runtime_configuration.steam_environment_data.cmd_steam_reaper,
            "/steamapps/common/Steam Linux Runtime/ubuntu12_32/reaper",
        )

    def test_does_not_override_existing_reaper_command(self):
        self.runtime_configuration.steam_environment_data.cmd_steam_reaper = (
            "/custom/reaper"
        )
        self.feature.apply_configuration(self.base_configuration, self.runtime_configuration)
        self.assertEqual(
            self.runtime_configuration.steam_environment_data.cmd_steam_reaper,
            "/custom/reaper",
        )

    def test_uses_custom_default_wrapper_command_property_value(self):
        configuration = dict(self.base_configuration)
        configuration["STEAM_DEFAULT_WRAPPER_COMMAND"] = "custom/wrapper-cmd"
        self.feature.apply_configuration(configuration, self.runtime_configuration)
        self.assertEqual(
            self.runtime_configuration.steam_environment_data.cmd_steam_wrapper,
            "/steamapps/common/Steam Linux Runtime/custom/wrapper-cmd",
        )


class TestSteamToolsPipelineWrappers(unittest.TestCase):
    def setUp(self):
        self.feature = SteamTools()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.steam_environment_data.steam_base_folder = "/steam"

    def test_no_wrappers_added_when_all_disabled(self):
        self.feature.apply_configuration(
            {
                "STEAM_USE_WRAPPER": False,
                "STEAM_USE_REAPER": False,
                "STEAM_USE_SNIPER": False,
            },
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)

    def test_default_configuration_enables_reaper_and_sniper_but_not_wrapper(self):
        # STEAM_USE_WRAPPER defaults to False; STEAM_USE_REAPER/SNIPER default to True.
        self.feature.apply_configuration({}, self.runtime_configuration)
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(len(wrappers), 2)

    def test_only_wrapper_added_when_only_wrapper_enabled(self):
        self.feature.apply_configuration(
            {
                "STEAM_USE_WRAPPER": True,
                "STEAM_USE_REAPER": False,
                "STEAM_USE_SNIPER": False,
            },
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(len(wrappers), 1)
        base_command = Command.from_string("game.exe")
        result = wrappers[0].wrapper(base_command, self.runtime_configuration)
        self.assertTrue(
            result.get_full_command().startswith(
                self.runtime_configuration.steam_environment_data.cmd_steam_wrapper
            )
        )

    def test_only_reaper_added_when_only_reaper_enabled(self):
        self.feature.apply_configuration(
            {
                "STEAM_USE_WRAPPER": False,
                "STEAM_USE_REAPER": True,
                "STEAM_USE_SNIPER": False,
            },
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(len(wrappers), 1)
        base_command = Command.from_string("game.exe")
        result = wrappers[0].wrapper(base_command, self.runtime_configuration)
        self.assertTrue(
            result.get_full_command().startswith(
                self.runtime_configuration.steam_environment_data.cmd_steam_reaper
            )
        )

    def test_only_sniper_added_when_only_sniper_enabled(self):
        self.feature.apply_configuration(
            {
                "STEAM_USE_WRAPPER": False,
                "STEAM_USE_REAPER": False,
                "STEAM_USE_SNIPER": True,
            },
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(len(wrappers), 1)
        base_command = Command.from_string("game.exe")
        result = wrappers[0].wrapper(base_command, self.runtime_configuration)
        self.assertTrue(
            result.get_full_command().startswith(
                self.runtime_configuration.steam_environment_data.cmd_steam_sniper
            )
        )

    def test_all_three_added_in_wrapper_reaper_sniper_order_when_all_enabled(self):
        self.feature.apply_configuration(
            {
                "STEAM_USE_WRAPPER": True,
                "STEAM_USE_REAPER": True,
                "STEAM_USE_SNIPER": True,
            },
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(len(wrappers), 3)
        base_command = Command.from_string("game.exe")
        wrapper_result = wrappers[0].wrapper(base_command, self.runtime_configuration)
        reaper_result = wrappers[1].wrapper(base_command, self.runtime_configuration)
        sniper_result = wrappers[2].wrapper(base_command, self.runtime_configuration)
        env = self.runtime_configuration.steam_environment_data
        self.assertTrue(wrapper_result.get_full_command().startswith(env.cmd_steam_wrapper))
        self.assertTrue(reaper_result.get_full_command().startswith(env.cmd_steam_reaper))
        self.assertTrue(sniper_result.get_full_command().startswith(env.cmd_steam_sniper))

    def test_wrapper_innermost_and_sniper_outermost_when_chained(self):
        self.runtime_configuration.steam_environment_data.steam_game_id = "123"
        self.feature.apply_configuration(
            {
                "STEAM_USE_WRAPPER": True,
                "STEAM_USE_REAPER": True,
                "STEAM_USE_SNIPER": True,
            },
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        base_command = Command.from_string("game.exe")
        result = base_command
        for wrapper in wrappers:
            result = wrapper.wrap(
                result,
                self.runtime_configuration,
                command_category=CommandCategory.GAME,
                logger=self.feature.logger,
            )
        full_command = result.get_full_command()
        env = self.runtime_configuration.steam_environment_data
        assert env.cmd_steam_wrapper is not None
        assert env.cmd_steam_reaper is not None
        assert env.cmd_steam_sniper is not None
        sniper_index = full_command.index(env.cmd_steam_sniper)
        reaper_index = full_command.index(env.cmd_steam_reaper)
        wrapper_index = full_command.index(env.cmd_steam_wrapper)
        game_index = full_command.index("game.exe")
        # Sniper wraps everything (outermost), wrapper is closest to the game
        # command (innermost).
        self.assertTrue(sniper_index < reaper_index < wrapper_index < game_index)

    def test_reaper_wrapper_includes_steamlaunch_appid_with_game_identifier(self):
        self.runtime_configuration.steam_environment_data.steam_game_id = "570"
        self.feature.apply_configuration(
            {"STEAM_USE_WRAPPER": False, "STEAM_USE_REAPER": True, "STEAM_USE_SNIPER": False},
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        base_command = Command.from_string("game.exe")
        result = wrappers[0].wrapper(base_command, self.runtime_configuration)
        full_command = result.get_full_command()
        self.assertIn("SteamLaunch", full_command)
        self.assertIn("AppId=570", full_command)

    def test_sniper_wrapper_applies_only_to_game_category(self):
        self.feature.apply_configuration(
            {"STEAM_USE_WRAPPER": False, "STEAM_USE_REAPER": False, "STEAM_USE_SNIPER": True},
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        sniper_wrapper = wrappers[0]
        self.assertEqual(sniper_wrapper.applies_for, [CommandCategory.GAME])
        self.assertTrue(sniper_wrapper.use_in_script)

    def test_wrapper_and_reaper_apply_for_script_and_game_categories(self):
        self.feature.apply_configuration(
            {"STEAM_USE_WRAPPER": True, "STEAM_USE_REAPER": True, "STEAM_USE_SNIPER": False},
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(
            wrappers[0].applies_for, [CommandCategory.SCRIPT, CommandCategory.GAME]
        )
        self.assertEqual(
            wrappers[1].applies_for, [CommandCategory.SCRIPT, CommandCategory.GAME]
        )


if __name__ == "__main__":
    _ = unittest.main()
