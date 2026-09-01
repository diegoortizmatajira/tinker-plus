import unittest

from features.umu_runner import UmuRunner
from model import Command, CommandCategory, RuntimeConfiguration


class TestUmuRunnerApplyConfiguration(unittest.TestCase):
    def setUp(self):
        self.feature = UmuRunner()
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_adds_wrapper_when_enabled_and_binary_set(self):
        self.feature.apply_configuration(
            {"UMU_RUN_ENABLED": True, "UMU_RUN_BINARY": "umu-run"},
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(len(wrappers), 1)

    def test_no_wrapper_when_disabled_and_binary_set(self):
        self.feature.apply_configuration(
            {"UMU_RUN_ENABLED": False, "UMU_RUN_BINARY": "umu-run"},
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)

    def test_no_wrapper_when_enabled_but_binary_empty(self):
        self.feature.apply_configuration(
            {"UMU_RUN_ENABLED": True, "UMU_RUN_BINARY": ""},
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)

    def test_no_wrapper_when_disabled_and_binary_empty(self):
        self.feature.apply_configuration(
            {"UMU_RUN_ENABLED": False, "UMU_RUN_BINARY": ""},
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)

    def test_default_configuration_does_not_add_wrapper(self):
        # UMU_RUN_ENABLED defaults to False, so even with the default binary
        # path ("umu-run") configured, no wrapper should be added.
        self.feature.apply_configuration({}, self.runtime_configuration)
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)

    def test_wrapper_applies_for_game_and_compatibility_tool_categories(self):
        self.feature.apply_configuration(
            {"UMU_RUN_ENABLED": True, "UMU_RUN_BINARY": "umu-run"},
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        self.assertEqual(
            wrappers[0].applies_for,
            [CommandCategory.GAME, CommandCategory.COMPATIBILITY_TOOL],
        )

    def test_wrapper_invokes_configured_binary_with_double_dash(self):
        self.feature.apply_configuration(
            {"UMU_RUN_ENABLED": True, "UMU_RUN_BINARY": "/opt/umu/umu-run"},
            self.runtime_configuration,
        )
        wrappers = self.runtime_configuration.pipeline_wrappers
        assert wrappers is not None
        base_command = Command.from_string("game.exe")
        wrapped_command = wrappers[0].wrap(
            base_command,
            self.runtime_configuration,
            command_category=CommandCategory.GAME,
            logger=self.feature.logger,
        )
        self.assertEqual(
            wrapped_command.get_full_command(), "/opt/umu/umu-run -- game.exe"
        )


class TestUmuRunnerBeforeExecution(unittest.TestCase):
    def setUp(self):
        self.feature = UmuRunner()
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_sets_wineprefix_from_prefix_path_when_enabled_and_binary_set(self):
        self.runtime_configuration.prefix_path = "/compatdata/123/pfx"
        self.feature.before_execution(
            {"UMU_RUN_ENABLED": True, "UMU_RUN_BINARY": "umu-run"},
            self.runtime_configuration,
        )
        assert self.runtime_configuration.environment_variables is not None
        self.assertEqual(
            self.runtime_configuration.environment_variables["WINEPREFIX"],
            "/compatdata/123/pfx",
        )

    def test_defaults_wineprefix_to_dot_when_no_prefix_path(self):
        self.runtime_configuration.prefix_path = None
        self.feature.before_execution(
            {"UMU_RUN_ENABLED": True, "UMU_RUN_BINARY": "umu-run"},
            self.runtime_configuration,
        )
        assert self.runtime_configuration.environment_variables is not None
        self.assertEqual(
            self.runtime_configuration.environment_variables["WINEPREFIX"], "."
        )

    def test_does_not_set_wineprefix_when_disabled(self):
        self.runtime_configuration.prefix_path = "/compatdata/123/pfx"
        self.feature.before_execution(
            {"UMU_RUN_ENABLED": False, "UMU_RUN_BINARY": "umu-run"},
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.environment_variables)

    def test_does_not_set_wineprefix_when_binary_empty(self):
        self.runtime_configuration.prefix_path = "/compatdata/123/pfx"
        self.feature.before_execution(
            {"UMU_RUN_ENABLED": True, "UMU_RUN_BINARY": ""},
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.environment_variables)


if __name__ == "__main__":
    _ = unittest.main()
