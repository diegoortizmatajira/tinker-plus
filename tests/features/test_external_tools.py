import unittest

from features.external_tools import ExternalTools
from model import Command, RuntimeConfiguration


class TestExternalToolsApplyConfiguration(unittest.TestCase):
    def setUp(self):
        self.feature = ExternalTools()
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_no_wrappers_added_when_all_tools_disabled(self):
        self.feature.apply_configuration({}, self.runtime_configuration)
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)

    def test_gamemoderun_enabled_adds_wrapper(self):
        self.feature.apply_configuration(
            {"GAMEMODERUN_ENABLED": True}, self.runtime_configuration
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(len(wrappers), 1)
        self.assertIsNone(wrappers[0].applies_for)
        game_command = Command.from_string("game.exe")
        wrapped = wrappers[0].wrapper(game_command, self.runtime_configuration)
        self.assertEqual(wrapped.get_chain_command(), ["gamemoderun", "game.exe"])

    def test_gamemoderun_disabled_adds_no_wrapper(self):
        self.feature.apply_configuration(
            {"GAMEMODERUN_ENABLED": False}, self.runtime_configuration
        )
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)

    def test_gamescope_enabled_adds_wrapper_with_args(self):
        self.feature.apply_configuration(
            {"GAMESCOPE_ENABLED": True, "GAMESCOPE_ARGS": "-W 1920"},
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(len(wrappers), 1)
        self.assertIsNone(wrappers[0].applies_for)
        game_command = Command.from_string("game.exe")
        wrapped = wrappers[0].wrapper(game_command, self.runtime_configuration)
        self.assertEqual(
            wrapped.get_chain_command(),
            ["gamescope", "-W", "1920", "--", "game.exe"],
        )

    def test_gamescope_enabled_without_args_defaults_to_empty_args(self):
        self.feature.apply_configuration(
            {"GAMESCOPE_ENABLED": True}, self.runtime_configuration
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        game_command = Command.from_string("game.exe")
        wrapped = wrappers[0].wrapper(game_command, self.runtime_configuration)
        self.assertEqual(
            wrapped.get_chain_command(), ["gamescope", "--", "game.exe"]
        )

    def test_gamescope_disabled_adds_no_wrapper(self):
        self.feature.apply_configuration(
            {"GAMESCOPE_ENABLED": False}, self.runtime_configuration
        )
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)

    def test_mangohud_enabled_adds_wrapper(self):
        self.feature.apply_configuration(
            {"MANGOHUD_ENABLED": True}, self.runtime_configuration
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(len(wrappers), 1)
        self.assertIsNone(wrappers[0].applies_for)
        game_command = Command.from_string("game.exe")
        wrapped = wrappers[0].wrapper(game_command, self.runtime_configuration)
        self.assertEqual(wrapped.get_chain_command(), ["mangohud", "game.exe"])

    def test_mangohud_disabled_adds_no_wrapper(self):
        self.feature.apply_configuration(
            {"MANGOHUD_ENABLED": False}, self.runtime_configuration
        )
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)

    def test_multiple_tools_enabled_adds_multiple_wrappers_in_order(self):
        self.feature.apply_configuration(
            {
                "GAMEMODERUN_ENABLED": True,
                "GAMESCOPE_ENABLED": True,
                "MANGOHUD_ENABLED": True,
            },
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(len(wrappers), 3)

    def test_external_terminal_command_template_defaults_when_not_configured(self):
        self.feature.apply_configuration({}, self.runtime_configuration)
        self.assertEqual(
            self.runtime_configuration.external_terminal_command_template,
            ["ghostty", "-e", "/bin/bash", "-c", "{command} && sleep 5"],
        )

    def test_external_terminal_command_template_uses_custom_value(self):
        self.feature.apply_configuration(
            {
                "EXTERNAL_TERMINAL_COMMAND_TEMPLATE": [
                    "xterm",
                    "-e",
                    "{command}",
                ]
            },
            self.runtime_configuration,
        )
        self.assertEqual(
            self.runtime_configuration.external_terminal_command_template,
            ["xterm", "-e", "{command}"],
        )

    def test_returns_the_runtime_configuration(self):
        result = self.feature.apply_configuration({}, self.runtime_configuration)
        self.assertIs(result, self.runtime_configuration)


if __name__ == "__main__":
    _ = unittest.main()
