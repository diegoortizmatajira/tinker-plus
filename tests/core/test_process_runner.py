import logging
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from core.process_runner import ProcessRunner
from model import Command, RuntimeConfiguration

TEST_LOGGER = logging.getLogger("test")


class TestRunInWinePrefix(unittest.TestCase):
    def test_raises_when_prefix_path_not_set(self):
        runtime_configuration = RuntimeConfiguration.empty()
        with self.assertRaises(RuntimeError):
            ProcessRunner.run_in_wine_prefix(
                Command.from_string("winecfg"), runtime_configuration, TEST_LOGGER
            )

    def test_dry_run_without_capture_returns_true(self):
        runtime_configuration = RuntimeConfiguration.empty()
        runtime_configuration.prefix_path = "/tmp/fake-prefix"
        result = ProcessRunner.run_in_wine_prefix(
            Command.from_string("winecfg"), runtime_configuration, TEST_LOGGER
        )
        self.assertTrue(result)

    def test_dry_run_with_capture_returns_true_and_placeholder_output(self):
        runtime_configuration = RuntimeConfiguration.empty()
        runtime_configuration.prefix_path = "/tmp/fake-prefix"
        result = ProcessRunner.run_in_wine_prefix(
            Command.from_string("winecfg"), runtime_configuration, TEST_LOGGER, True
        )
        self.assertEqual(result, (True, "win10"))


class TestAssembleCommandStr(unittest.TestCase):
    def test_no_wrappers_returns_original_command(self):
        runtime_configuration = RuntimeConfiguration.empty()
        command = Command.from_string("game.exe")
        result = ProcessRunner.assemble_command_str(
            command, runtime_configuration, TEST_LOGGER
        )
        self.assertEqual(result.get_full_command(), "game.exe")

    def test_wrappers_applied_in_reverse_order(self):
        from model import CommandWrapper, CommandCategory

        runtime_configuration = RuntimeConfiguration.empty()
        command = Command.from_string("game.exe", category=CommandCategory.GAME)
        runtime_configuration.add_pipeline_wrapper(
            CommandWrapper.from_command_str("first")
        )
        runtime_configuration.add_pipeline_wrapper(
            CommandWrapper.from_command_str("second")
        )
        result = ProcessRunner.assemble_command_str(
            command, runtime_configuration, TEST_LOGGER
        )
        # "second" (last added) wraps innermost, "first" wraps outermost.
        self.assertEqual(result.get_full_command(), "first second game.exe")


class TestRunCommandWithCompatibilityTool(unittest.TestCase):
    def test_dry_run_returns_true_without_executing(self):
        runtime_configuration = RuntimeConfiguration.empty()
        result = ProcessRunner.run_command_with_compatibility_tool(
            Command.from_string("game.exe"), runtime_configuration, TEST_LOGGER
        )
        self.assertTrue(result)


class TestRunChainCommand(unittest.TestCase):
    def test_dry_run_returns_none(self):
        result = ProcessRunner.run_chain_command(
            ["echo", "hello"], TEST_LOGGER, dry_run=True
        )
        self.assertIsNone(result)

    def test_runs_real_command_and_captures_output(self):
        process = ProcessRunner.run_chain_command(["echo", "hello"], TEST_LOGGER)
        self.assertIsNotNone(process)
        assert process is not None
        stdout, _ = process.communicate(timeout=5)
        self.assertEqual(stdout.decode().strip(), "hello")


class TestRunInExternalTerminal(unittest.TestCase):
    def test_raises_when_no_template_provided(self):
        with self.assertRaises(RuntimeError):
            ProcessRunner.run_in_external_terminal(None, "game.exe", TEST_LOGGER)

    def test_dry_run_returns_none(self):
        result = ProcessRunner.run_in_external_terminal(
            ["echo", "{command}"], "game.exe", TEST_LOGGER, dry_run=True
        )
        self.assertIsNone(result)


class TestRunWithPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.tmp_dir, ignore_errors=True))

    def test_dry_run_does_not_create_working_directory(self):
        runtime_configuration = RuntimeConfiguration.empty()
        custom_cwd = str(self.tmp_dir / "does_not_exist_yet")
        command = Command.from_string("game.exe", cwd=custom_cwd)
        result = ProcessRunner.run_with_pipeline(
            command, runtime_configuration, TEST_LOGGER
        )
        self.assertIsNone(result)
        self.assertFalse(Path(custom_cwd).exists())

    def test_non_dry_run_creates_working_directory(self):
        runtime_configuration = RuntimeConfiguration.empty()
        runtime_configuration.dry_run = False
        custom_cwd = str(self.tmp_dir / "created_by_run")
        command = Command.from_string("echo hello", cwd=custom_cwd)
        process = ProcessRunner.run_with_pipeline(
            command, runtime_configuration, TEST_LOGGER
        )
        self.assertTrue(Path(custom_cwd).exists())
        self.assertIsNotNone(process)
        assert process is not None
        _ = process.communicate(timeout=5)


class TestWaitAndLog(unittest.TestCase):
    def test_waits_and_logs_pid_and_exit_code(self):
        process = MagicMock(spec=subprocess.Popen)
        process.pid = 4242
        process.wait.return_value = 0
        process.__enter__.return_value = process
        process.__exit__.return_value = False

        result = ProcessRunner.wait_and_log(process, TEST_LOGGER, "before startup process")
        self.assertEqual(result, 0)
        process.wait.assert_called_once()


if __name__ == "__main__":
    _ = unittest.main()
