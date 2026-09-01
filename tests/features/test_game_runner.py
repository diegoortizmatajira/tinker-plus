import logging
import os
import unittest
from unittest.mock import MagicMock, patch

from features.game_runner import GameRunner
from model import Command, CommandCategory, RuntimeConfiguration

TEST_LOGGER = logging.getLogger("test")


class TestApplyConfiguration(unittest.TestCase):
    def setUp(self):
        self.runner = GameRunner()
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_defaults_to_echo_when_no_executable_command_set(self):
        self.runner.apply_configuration({}, self.runtime_configuration)
        assert self.runtime_configuration.game_executable_command is not None
        self.assertEqual(
            self.runtime_configuration.game_executable_command.command, "echo"
        )

    def test_custom_exe_and_args_override_command(self):
        self.runtime_configuration.game_executable_command = Command.from_string(
            "echo", category=CommandCategory.GAME
        )
        self.runner.apply_configuration(
            {"GAME_CUSTOM_EXE": "game.exe", "GAME_CUSTOM_ARGS": "--fullscreen"},
            self.runtime_configuration,
        )
        command = self.runtime_configuration.game_executable_command
        assert command is not None
        self.assertEqual(command.command, "game.exe")
        self.assertEqual(command.get_full_command(), "game.exe --fullscreen")

    def test_custom_cwd_takes_priority_over_steam_paths(self):
        self.runtime_configuration.steam_environment_data.steam_compat_install_path = (
            "/steam/install"
        )
        self.runner.apply_configuration(
            {"GAME_CUSTOM_CWD": "/custom/cwd"}, self.runtime_configuration
        )
        command = self.runtime_configuration.game_executable_command
        assert command is not None
        self.assertEqual(command.cwd, "/custom/cwd")

    def test_cwd_falls_back_to_steam_compat_install_path(self):
        self.runtime_configuration.steam_environment_data.steam_compat_install_path = (
            "/steam/install"
        )
        self.runner.apply_configuration({}, self.runtime_configuration)
        command = self.runtime_configuration.game_executable_command
        assert command is not None
        self.assertEqual(command.cwd, "/steam/install")

    def test_forks_only_flag_is_applied(self):
        self.runner.apply_configuration(
            {"GAME_RUN_FORKS_ONLY": True}, self.runtime_configuration
        )
        self.assertTrue(self.runtime_configuration.execute_forks_only)

    def test_run_with_script_defaults_to_true(self):
        self.runner.apply_configuration({}, self.runtime_configuration)
        self.assertTrue(self.runner.run_with_script)


class TestGetRunSequence(unittest.TestCase):
    def setUp(self):
        self.runner = GameRunner()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.game_executable_command = Command.from_string(
            "game.exe", category=CommandCategory.GAME
        )

    def test_includes_game_command_by_default(self):
        sequence = self.runner.get_run_sequence(
            [CommandCategory.GAME], self.runtime_configuration
        )
        self.assertEqual(sequence, [self.runtime_configuration.game_executable_command])

    def test_excludes_game_command_when_forks_only(self):
        self.runtime_configuration.execute_forks_only = True
        sequence = self.runner.get_run_sequence(
            [CommandCategory.GAME], self.runtime_configuration
        )
        self.assertEqual(sequence, [])

    def test_includes_trainer_fork_commands_when_enabled(self):
        trainer_command = Command.from_string(
            "trainer.exe", category=CommandCategory.TRAINER
        )
        self.runtime_configuration.add_fork_command(trainer_command)
        self.runtime_configuration.execute_trainers = True
        sequence = self.runner.get_run_sequence(
            [CommandCategory.TRAINER], self.runtime_configuration
        )
        self.assertEqual(sequence, [trainer_command])

    def test_excludes_trainer_fork_commands_when_disabled(self):
        trainer_command = Command.from_string(
            "trainer.exe", category=CommandCategory.TRAINER
        )
        self.runtime_configuration.add_fork_command(trainer_command)
        self.runtime_configuration.execute_trainers = False
        sequence = self.runner.get_run_sequence(
            [CommandCategory.TRAINER], self.runtime_configuration
        )
        self.assertEqual(sequence, [])

    def test_orders_commands_by_requested_category_order(self):
        trainer_command = Command.from_string(
            "trainer.exe", category=CommandCategory.TRAINER
        )
        self.runtime_configuration.add_fork_command(trainer_command)
        sequence = self.runner.get_run_sequence(
            [CommandCategory.TRAINER, CommandCategory.GAME], self.runtime_configuration
        )
        self.assertEqual(
            sequence, [trainer_command, self.runtime_configuration.game_executable_command]
        )


class TestRunGame(unittest.TestCase):
    def setUp(self):
        self.runner = GameRunner()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.command = Command.from_string("game.exe", category=CommandCategory.GAME)

    @patch("features.game_runner.ProcessRunner.run_with_pipeline")
    def test_stores_process_handle_on_success(self, mock_run: MagicMock):
        fake_process = MagicMock()
        fake_process.pid = 1234
        mock_run.return_value = fake_process
        self.runner.run_game(self.runtime_configuration, self.command)
        self.assertIs(self.runner.game_process, fake_process)

    @patch("features.game_runner.ProcessRunner.run_with_pipeline")
    def test_raises_when_launch_fails(self, mock_run: MagicMock):
        mock_run.return_value = None
        with self.assertRaises(RuntimeError):
            self.runner.run_game(self.runtime_configuration, self.command)


class TestRunTrainer(unittest.TestCase):
    def setUp(self):
        self.runner = GameRunner()
        self.runner.trainer_process_list = []
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.command = Command.from_string(
            "trainer.exe", category=CommandCategory.TRAINER
        )

    @patch("features.game_runner.sleep")
    @patch("features.game_runner.ProcessRunner.run_with_pipeline")
    def test_appends_process_to_trainer_list_on_success(
        self, mock_run: MagicMock, mock_sleep: MagicMock
    ):
        fake_process = MagicMock()
        fake_process.pid = 5678
        mock_run.return_value = fake_process
        self.runner.run_trainer(self.runtime_configuration, self.command)
        self.assertEqual(self.runner.trainer_process_list, [fake_process])
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("features.game_runner.sleep")
    @patch("features.game_runner.ProcessRunner.run_with_pipeline")
    def test_does_not_append_when_launch_fails(
        self, mock_run: MagicMock, _mock_sleep: MagicMock
    ):
        mock_run.return_value = None
        self.runner.run_trainer(self.runtime_configuration, self.command)
        self.assertEqual(self.runner.trainer_process_list, [])


class TestExecuteWithScript(unittest.TestCase):
    def setUp(self):
        self.runner = GameRunner()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.written_scripts: list[str] = []

    def tearDown(self):
        for path in self.written_scripts:
            if os.path.exists(path):
                os.remove(path)

    @patch("features.game_runner.ProcessRunner.assemble_command_str")
    def test_raises_when_no_commands_configured(self, mock_assemble: MagicMock):
        # No game executable command and no fork commands configured.
        self.runtime_configuration.game_executable_command = None
        with self.assertRaises(RuntimeError):
            self.runner.execute_with_script({}, self.runtime_configuration)
        mock_assemble.assert_not_called()

    @patch("features.game_runner.ProcessRunner.run_with_pipeline")
    @patch("features.game_runner.ProcessRunner.assemble_command_str")
    def test_single_command_runs_directly_without_script_file(
        self, mock_assemble: MagicMock, mock_run: MagicMock
    ):
        self.runtime_configuration.game_executable_command = Command.from_string(
            "game.exe", category=CommandCategory.GAME
        )
        mock_assemble.return_value = Command.from_string("game.exe")
        self.runner.execute_with_script({}, self.runtime_configuration)
        ran_command = mock_run.call_args[0][0]
        self.assertEqual(ran_command.command, "game.exe")

    @patch("features.game_runner.ProcessRunner.run_with_pipeline")
    @patch("features.game_runner.ProcessRunner.assemble_command_str")
    def test_multiple_commands_build_a_temporary_script(
        self, mock_assemble: MagicMock, mock_run: MagicMock
    ):
        self.runtime_configuration.game_executable_command = Command.from_string(
            "game.exe", category=CommandCategory.GAME
        )
        trainer_command = Command.from_string(
            "trainer.exe", category=CommandCategory.TRAINER
        )
        self.runtime_configuration.add_fork_command(trainer_command)
        mock_assemble.side_effect = lambda command, *_args, **_kwargs: command
        self.runner.execute_with_script({}, self.runtime_configuration)
        ran_command = mock_run.call_args[0][0]
        self.written_scripts.append(ran_command.command)
        self.assertTrue(os.path.exists(ran_command.command))
        content = open(ran_command.command, "rb").read().decode()
        self.assertIn("trainer.exe", content)
        self.assertIn("game.exe", content)
        self.assertTrue(os.access(ran_command.command, os.X_OK))


class TestExecuteInPipeline(unittest.TestCase):
    def setUp(self):
        self.runner = GameRunner()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.game_executable_command = Command.from_string(
            "game.exe", category=CommandCategory.GAME
        )

    @patch.object(GameRunner, "execute_with_script")
    def test_delegates_to_script_execution_when_enabled(self, mock_script: MagicMock):
        self.runner.run_with_script = True
        self.runner.execute_in_pipeline({}, self.runtime_configuration)
        mock_script.assert_called_once_with({}, self.runtime_configuration)

    @patch.object(GameRunner, "run_trainer")
    @patch.object(GameRunner, "run_game")
    def test_runs_commands_directly_when_script_disabled(
        self, mock_run_game: MagicMock, mock_run_trainer: MagicMock
    ):
        self.runner.run_with_script = False
        self.runner.execute_in_pipeline({}, self.runtime_configuration)
        mock_run_game.assert_called_once()
        mock_run_trainer.assert_not_called()

    def test_resets_process_state_at_start(self):
        self.runner.run_with_script = False
        self.runner.game_process = MagicMock()
        self.runner.trainer_process_list = [MagicMock()]
        with patch.object(GameRunner, "run_game"):
            self.runner.execute_in_pipeline({}, self.runtime_configuration)
        self.assertEqual(self.runner.trainer_process_list, [])


class TestWaitForCompletion(unittest.TestCase):
    def setUp(self):
        self.runner = GameRunner()
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_waits_for_game_process(self):
        game_process = MagicMock()
        game_process.wait.return_value = 0
        game_process.__enter__.return_value = game_process
        game_process.__exit__.return_value = False
        self.runner.game_process = game_process
        self.runner.trainer_process_list = []
        self.runner.wait_for_completion({}, self.runtime_configuration)
        game_process.wait.assert_called_once()

    def test_waits_for_still_running_trainer_process(self):
        self.runner.game_process = None
        trainer_process = MagicMock()
        trainer_process.poll.return_value = None
        trainer_process.wait.return_value = 0
        self.runner.trainer_process_list = [trainer_process]
        self.runner.wait_for_completion({}, self.runtime_configuration)
        trainer_process.wait.assert_called_once()

    def test_logs_stderr_for_already_exited_failed_trainer(self):
        self.runner.game_process = None
        trainer_process = MagicMock()
        trainer_process.poll.return_value = 1
        trainer_process.stderr.read.return_value = b"boom"
        self.runner.trainer_process_list = [trainer_process]
        with self.assertLogs(level="ERROR"):
            self.runner.wait_for_completion({}, self.runtime_configuration)
        trainer_process.wait.assert_not_called()


if __name__ == "__main__":
    _ = unittest.main()
