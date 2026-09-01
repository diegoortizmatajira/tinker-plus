import unittest
from unittest.mock import MagicMock, patch

from features.context_commands import ContextCommands
from model import RuntimeConfiguration


class TestContextCommandsBeforeExecution(unittest.TestCase):
    def setUp(self):
        self.feature = ContextCommands()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False

        self.run_patcher = patch(
            "features.context_commands.ProcessRunner.run_chain_command"
        )
        self.mock_run = self.run_patcher.start()
        self.addCleanup(self.run_patcher.stop)

        self.wait_patcher = patch(
            "features.context_commands.ProcessRunner.wait_and_log"
        )
        self.mock_wait = self.wait_patcher.start()
        self.addCleanup(self.wait_patcher.stop)

    def test_skips_when_no_before_command_configured(self):
        self.feature.before_execution({}, self.runtime_configuration)
        self.mock_run.assert_not_called()
        self.mock_wait.assert_not_called()

    def test_runs_before_command_and_waits_on_process(self):
        fake_process = MagicMock()
        self.mock_run.return_value = fake_process
        self.feature.before_execution(
            {"CONTEXT_COMMAND_BEFORE_STARTUP": "echo hi"}, self.runtime_configuration
        )
        self.mock_run.assert_called_once_with(
            ["echo", "hi"], self.feature.logger, dry_run=False
        )
        self.mock_wait.assert_called_once_with(
            fake_process, self.feature.logger, "before startup process"
        )

    def test_does_not_wait_when_run_chain_command_returns_none(self):
        self.mock_run.return_value = None
        self.feature.before_execution(
            {"CONTEXT_COMMAND_BEFORE_STARTUP": "echo hi"}, self.runtime_configuration
        )
        self.mock_wait.assert_not_called()

    def test_forwards_dry_run_flag(self):
        self.runtime_configuration.dry_run = True
        self.mock_run.return_value = None
        self.feature.before_execution(
            {"CONTEXT_COMMAND_BEFORE_STARTUP": "echo hi"}, self.runtime_configuration
        )
        self.assertTrue(self.mock_run.call_args.kwargs["dry_run"])


class TestContextCommandsAfterExecution(unittest.TestCase):
    def setUp(self):
        self.feature = ContextCommands()
        self.runtime_configuration = RuntimeConfiguration.empty()
        self.runtime_configuration.dry_run = False

        self.run_patcher = patch(
            "features.context_commands.ProcessRunner.run_chain_command"
        )
        self.mock_run = self.run_patcher.start()
        self.addCleanup(self.run_patcher.stop)

        self.wait_patcher = patch(
            "features.context_commands.ProcessRunner.wait_and_log"
        )
        self.mock_wait = self.wait_patcher.start()
        self.addCleanup(self.wait_patcher.stop)

    def test_skips_when_no_after_command_configured(self):
        self.feature.after_execution({}, self.runtime_configuration)
        self.mock_run.assert_not_called()
        self.mock_wait.assert_not_called()

    def test_runs_after_command_and_waits_on_process(self):
        fake_process = MagicMock()
        self.mock_run.return_value = fake_process
        self.feature.after_execution(
            {"CONTEXT_COMMAND_AFTER_EXIT": "echo bye"}, self.runtime_configuration
        )
        self.mock_run.assert_called_once_with(
            ["echo", "bye"], self.feature.logger, dry_run=False
        )
        self.mock_wait.assert_called_once_with(
            fake_process, self.feature.logger, "after exit process"
        )

    def test_does_not_wait_when_run_chain_command_returns_none(self):
        self.mock_run.return_value = None
        self.feature.after_execution(
            {"CONTEXT_COMMAND_AFTER_EXIT": "echo bye"}, self.runtime_configuration
        )
        self.mock_wait.assert_not_called()

    def test_forwards_dry_run_flag(self):
        self.runtime_configuration.dry_run = True
        self.mock_run.return_value = None
        self.feature.after_execution(
            {"CONTEXT_COMMAND_AFTER_EXIT": "echo bye"}, self.runtime_configuration
        )
        self.assertTrue(self.mock_run.call_args.kwargs["dry_run"])


if __name__ == "__main__":
    _ = unittest.main()
