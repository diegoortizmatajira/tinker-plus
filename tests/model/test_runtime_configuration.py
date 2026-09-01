import unittest

from model.command import Command, CommandCategory
from model.command_wrapper import CommandWrapper
from model.runtime_configuration import RuntimeConfiguration


class TestRuntimeConfiguration(unittest.TestCase):
    def setUp(self):
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_empty_has_dry_run_enabled(self):
        self.assertTrue(self.runtime_configuration.dry_run)
        self.assertEqual(self.runtime_configuration.game_info.game_id, "unknown")

    def test_get_game_identifier_prefers_game_id_over_app_id(self):
        self.runtime_configuration.steam_environment_data.steam_game_id = "123"
        self.runtime_configuration.steam_environment_data.steam_app_id = "456"
        self.assertEqual(self.runtime_configuration.get_game_identifier(), "123")

    def test_get_game_identifier_falls_back_to_app_id(self):
        self.runtime_configuration.steam_environment_data.steam_game_id = None
        self.runtime_configuration.steam_environment_data.steam_app_id = "456"
        self.assertEqual(self.runtime_configuration.get_game_identifier(), "456")

    def test_get_game_identifier_falls_back_to_unknown(self):
        self.runtime_configuration.steam_environment_data.steam_game_id = None
        self.runtime_configuration.steam_environment_data.steam_app_id = None
        self.assertEqual(self.runtime_configuration.get_game_identifier(), "unknown")

    def test_get_game_files_path(self):
        self.runtime_configuration.steam_environment_data.steam_compat_install_path = (
            "/games/foo"
        )
        self.assertEqual(
            self.runtime_configuration.get_game_files_path(), "/games/foo"
        )

    def test_get_compat_data_path(self):
        self.runtime_configuration.steam_environment_data.steam_compat_data_path = (
            "/compatdata/123"
        )
        self.assertEqual(
            self.runtime_configuration.get_compat_data_path(), "/compatdata/123"
        )

    def test_add_fork_command_initializes_list(self):
        self.assertIsNone(self.runtime_configuration.fork_commands)
        command = Command.from_string("trainer.exe")
        self.runtime_configuration.add_fork_command(command)
        self.assertEqual(self.runtime_configuration.fork_commands, [command])

    def test_add_fork_command_appends_to_existing_list(self):
        first = Command.from_string("trainer1.exe")
        second = Command.from_string("trainer2.exe")
        self.runtime_configuration.add_fork_command(first)
        self.runtime_configuration.add_fork_command(second)
        self.assertEqual(self.runtime_configuration.fork_commands, [first, second])

    def test_set_environment_variable_initializes_dict(self):
        self.assertIsNone(self.runtime_configuration.environment_variables)
        self.runtime_configuration.set_environment_variable("KEY", "value")
        self.assertEqual(
            self.runtime_configuration.environment_variables, {"KEY": "value"}
        )

    def test_set_environment_variable_overwrites_existing_key(self):
        self.runtime_configuration.set_environment_variable("KEY", "first")
        self.runtime_configuration.set_environment_variable("KEY", "second")
        self.assertEqual(
            self.runtime_configuration.environment_variables, {"KEY": "second"}
        )

    def test_add_pipeline_wrapper_initializes_list(self):
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)
        wrapper = CommandWrapper(wrapper=lambda cmd, _: cmd)
        self.runtime_configuration.add_pipeline_wrapper(wrapper)
        self.assertEqual(self.runtime_configuration.pipeline_wrappers, [wrapper])

    def test_has_trainers_false_when_no_fork_commands(self):
        self.assertFalse(self.runtime_configuration.has_trainers)

    def test_has_trainers_false_when_fork_commands_have_no_trainer_category(self):
        self.runtime_configuration.add_fork_command(
            Command.from_string("tool.exe", category=CommandCategory.COMPATIBILITY_TOOL)
        )
        self.assertFalse(self.runtime_configuration.has_trainers)

    def test_has_trainers_true_when_a_trainer_command_exists(self):
        self.runtime_configuration.add_fork_command(
            Command.from_string("trainer.exe", category=CommandCategory.TRAINER)
        )
        self.assertTrue(self.runtime_configuration.has_trainers)

    def test_set_debugger_sets_expected_environment_variables(self):
        command = Command.from_string("/prefix/drive_c/trainer/CustomTrainer.exe")
        self.runtime_configuration.set_debugger(command)
        env = self.runtime_configuration.environment_variables
        self.assertIsNotNone(env)
        assert env is not None
        self.assertEqual(env["PROTON_REMOTE_DEBUG_CMD"], command.get_full_command())
        self.assertTrue(env["PRESSURE_VESSEL_FILESYSTEMS_RW"].endswith("/trainer"))

    def test_reset_clears_run_specific_state(self):
        self.runtime_configuration.add_fork_command(Command.from_string("trainer.exe"))
        self.runtime_configuration.execute_trainers = False
        self.runtime_configuration.set_environment_variable("KEY", "value")
        self.runtime_configuration.add_pipeline_wrapper(
            CommandWrapper(wrapper=lambda cmd, _: cmd)
        )
        self.runtime_configuration.reset()
        self.assertIsNone(self.runtime_configuration.fork_commands)
        self.assertTrue(self.runtime_configuration.execute_trainers)
        self.assertIsNone(self.runtime_configuration.environment_variables)
        self.assertIsNone(self.runtime_configuration.pipeline_wrappers)


if __name__ == "__main__":
    _ = unittest.main()
