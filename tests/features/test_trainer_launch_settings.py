import unittest
from unittest.mock import MagicMock, patch

from features.trainer_launch_settings import TrainerLaunchSettings
from model import RuntimeConfiguration


class TestTrainerLaunchSettingsApplyConfiguration(unittest.TestCase):
    def setUp(self):
        self.feature = TrainerLaunchSettings()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False

    def test_no_trainer_source_configured_does_nothing(self):
        self.feature.apply_configuration({}, self.runtime_configuration)
        self.assertIsNone(self.runtime_configuration.fork_commands)
        self.assertIsNone(self.runtime_configuration.environment_variables)

    def test_custom_trainer_forked_when_enabled_and_not_debugger(self):
        self.feature.apply_configuration(
            {
                "TRAINER_ENABLED": True,
                "TRAINER_CUSTOM_EXE": "/trainers/custom.exe",
                "TRAINER_CUSTOM_ARGS": "--foo",
                "TRAINER_AS_DEBUGGER": False,
            },
            self.runtime_configuration,
        )
        assert self.runtime_configuration.fork_commands is not None
        self.assertEqual(len(self.runtime_configuration.fork_commands), 1)
        command = self.runtime_configuration.fork_commands[0]
        self.assertEqual(command.command, "/trainers/custom.exe")
        self.assertEqual(command.get_full_command(), "/trainers/custom.exe --foo")
        self.assertTrue(self.runtime_configuration.execute_trainers)

    def test_custom_trainer_as_debugger_sets_debugger_instead_of_fork(self):
        self.feature.apply_configuration(
            {
                "TRAINER_ENABLED": True,
                "TRAINER_CUSTOM_EXE": "/trainers/custom.exe",
                "TRAINER_AS_DEBUGGER": True,
            },
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.fork_commands)
        assert self.runtime_configuration.environment_variables is not None
        self.assertEqual(
            self.runtime_configuration.environment_variables[
                "PROTON_REMOTE_DEBUG_CMD"
            ],
            "/trainers/custom.exe",
        )

    def test_custom_trainer_skipped_when_trainer_disabled(self):
        self.feature.apply_configuration(
            {
                "TRAINER_ENABLED": False,
                "TRAINER_CUSTOM_EXE": "/trainers/custom.exe",
            },
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.fork_commands)

    def test_custom_trainer_skipped_when_no_exe_configured(self):
        self.feature.apply_configuration(
            {"TRAINER_ENABLED": True},
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.fork_commands)

    def test_wemod_forked_with_gameid_args_when_enabled_and_gameid_set(self):
        self.feature.apply_configuration(
            {
                "TRAINER_WEMOD_ENABLED": True,
                "TRAINER_WEMOD_EXE": "/wemod/WeMod.exe",
                "TRAINER_WEMOD_GAMEID": "12345",
                "TRAINER_AS_DEBUGGER": False,
            },
            self.runtime_configuration,
        )
        assert self.runtime_configuration.fork_commands is not None
        command = self.runtime_configuration.fork_commands[0]
        self.assertEqual(command.command, "/wemod/WeMod.exe")
        self.assertIn(
            "wemod://play?titleId=12345&gameId=12345", command.get_full_command()
        )

    def test_wemod_forked_without_gameid_when_open_without_gameid_true(self):
        self.feature.apply_configuration(
            {
                "TRAINER_WEMOD_ENABLED": True,
                "TRAINER_WEMOD_EXE": "/wemod/WeMod.exe",
                "TRAINER_WEMOD_OPEN_WITHOUT_GAMEID": True,
                "TRAINER_AS_DEBUGGER": False,
            },
            self.runtime_configuration,
        )
        assert self.runtime_configuration.fork_commands is not None
        command = self.runtime_configuration.fork_commands[0]
        self.assertEqual(command.get_full_command(), "/wemod/WeMod.exe")

    def test_wemod_skipped_when_no_gameid_and_open_without_gameid_false(self):
        self.feature.apply_configuration(
            {
                "TRAINER_WEMOD_ENABLED": True,
                "TRAINER_WEMOD_EXE": "/wemod/WeMod.exe",
            },
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.fork_commands)

    def test_wemod_skipped_when_not_enabled(self):
        self.feature.apply_configuration(
            {
                "TRAINER_WEMOD_EXE": "/wemod/WeMod.exe",
                "TRAINER_WEMOD_GAMEID": "12345",
            },
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.fork_commands)

    def test_cheat_engine_forked_with_file_when_configured(self):
        self.feature.apply_configuration(
            {
                "TRAINER_CHEAT_ENGINE_EXE": "/ce/cheatengine.exe",
                "TRAINER_CHEAT_ENGINE_FILE": "/tables/mytable.ct",
                "TRAINER_AS_DEBUGGER": False,
            },
            self.runtime_configuration,
        )
        assert self.runtime_configuration.fork_commands is not None
        command = self.runtime_configuration.fork_commands[0]
        self.assertEqual(command.command, "/ce/cheatengine.exe")
        self.assertIn("/tables/mytable.ct", command.get_full_command())

    def test_cheat_engine_forked_without_file_when_run_without_file_true(self):
        self.feature.apply_configuration(
            {
                "TRAINER_CHEAT_ENGINE_EXE": "/ce/cheatengine.exe",
                "TRAINER_CHEAT_ENGINE_RUN_WITHOUT_FILE": True,
                "TRAINER_AS_DEBUGGER": False,
            },
            self.runtime_configuration,
        )
        assert self.runtime_configuration.fork_commands is not None
        command = self.runtime_configuration.fork_commands[0]
        self.assertEqual(command.get_full_command(), "/ce/cheatengine.exe")

    def test_cheat_engine_skipped_when_no_file_and_run_without_file_false(self):
        self.feature.apply_configuration(
            {"TRAINER_CHEAT_ENGINE_EXE": "/ce/cheatengine.exe"},
            self.runtime_configuration,
        )
        self.assertIsNone(self.runtime_configuration.fork_commands)

    def test_all_three_sources_enabled_forks_all_three(self):
        self.feature.apply_configuration(
            {
                "TRAINER_ENABLED": True,
                "TRAINER_CUSTOM_EXE": "/trainers/custom.exe",
                "TRAINER_WEMOD_ENABLED": True,
                "TRAINER_WEMOD_EXE": "/wemod/WeMod.exe",
                "TRAINER_WEMOD_OPEN_WITHOUT_GAMEID": True,
                "TRAINER_CHEAT_ENGINE_EXE": "/ce/cheatengine.exe",
                "TRAINER_CHEAT_ENGINE_RUN_WITHOUT_FILE": True,
                "TRAINER_AS_DEBUGGER": False,
            },
            self.runtime_configuration,
        )
        assert self.runtime_configuration.fork_commands is not None
        self.assertEqual(len(self.runtime_configuration.fork_commands), 3)


class TestTrainerLaunchSettingsPreparePrefixForWemod(unittest.TestCase):
    def setUp(self):
        self.feature = TrainerLaunchSettings()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False
        self.runtime_configuration.steam_compatibility_tool = "GE-Proton10-25"
        self.runtime_configuration.steam_environment_data.steam_game_id = "123"

        self.run_chain_patcher = patch(
            "features.trainer_launch_settings.ProcessRunner.run_chain_command"
        )
        self.mock_run_chain = self.run_chain_patcher.start()
        self.addCleanup(self.run_chain_patcher.stop)

    def test_skips_when_no_compatibility_tool(self):
        self.runtime_configuration.steam_compatibility_tool = None
        with self.assertLogs(level="ERROR"):
            self.feature.prepare_prefix_for_wemod({}, self.runtime_configuration)
        self.mock_run_chain.assert_not_called()

    def test_runs_protontricks_with_proton_version_env(self):
        mock_process = MagicMock()
        mock_process.wait.return_value = 0
        self.mock_run_chain.return_value = mock_process
        self.feature.prepare_prefix_for_wemod({}, self.runtime_configuration)
        self.mock_run_chain.assert_called_once()
        call = self.mock_run_chain.call_args
        self.assertEqual(call.args[0], ["/usr/bin/protontricks", "123", "dotnet48"])
        self.assertEqual(
            call.kwargs["environment_variables"]["PROTON_VERSION"],
            "GE-Proton10-25",
        )
        self.assertEqual(call.kwargs["dry_run"], False)

    def test_raises_when_installer_exits_nonzero(self):
        mock_process = MagicMock()
        mock_process.wait.return_value = 1
        self.mock_run_chain.return_value = mock_process
        with self.assertRaises(RuntimeError):
            self.feature.prepare_prefix_for_wemod({}, self.runtime_configuration)

    def test_does_not_raise_when_run_chain_command_returns_none(self):
        self.mock_run_chain.return_value = None
        # Should complete without raising even though no process was started.
        self.feature.prepare_prefix_for_wemod({}, self.runtime_configuration)


if __name__ == "__main__":
    _ = unittest.main()
