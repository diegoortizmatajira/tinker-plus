import logging
import unittest

from model.command import Command, CommandCategory
from model.command_wrapper import CommandWrapper


class TestCommandWrapper(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test_logger")
        self.pipeline_command = Command.from_string("game.exe")

    def test_wrap_applies_for_default_category(self):
        wrapper = CommandWrapper(
            wrapper=lambda cmd, _: Command(["wrapped", cmd]),
        )
        result = wrapper.wrap(
            self.pipeline_command,
            None,
            command_category=CommandCategory.GAME,
            logger=self.logger,
        )
        self.assertEqual(result.get_full_command(), "wrapped game.exe")

    def test_wrap_skips_when_category_not_in_applies_for(self):
        wrapper = CommandWrapper(
            wrapper=lambda cmd, _: Command(["wrapped", cmd]),
            applies_for=[CommandCategory.TRAINER],
        )
        result = wrapper.wrap(
            self.pipeline_command,
            None,
            command_category=CommandCategory.GAME,
            logger=self.logger,
        )
        self.assertIs(result, self.pipeline_command)

    def test_wrap_skips_when_no_category_provided(self):
        wrapper = CommandWrapper(wrapper=lambda cmd, _: Command(["wrapped", cmd]))
        result = wrapper.wrap(self.pipeline_command, None, logger=self.logger)
        self.assertIs(result, self.pipeline_command)

    def test_wrap_applies_for_multiple_categories(self):
        wrapper = CommandWrapper(
            wrapper=lambda cmd, _: Command(["wrapped", cmd]),
            applies_for=[CommandCategory.GAME, CommandCategory.TRAINER],
        )
        for category in (CommandCategory.GAME, CommandCategory.TRAINER):
            with self.subTest(category=category):
                result = wrapper.wrap(
                    self.pipeline_command,
                    None,
                    command_category=category,
                    logger=self.logger,
                )
                self.assertEqual(result.get_full_command(), "wrapped game.exe")

    def test_wrap_skips_in_script_context_by_default(self):
        wrapper = CommandWrapper(
            wrapper=lambda cmd, _: Command(["wrapped", cmd]),
            applies_for=[CommandCategory.GAME],
        )
        result = wrapper.wrap(
            self.pipeline_command,
            None,
            command_category=CommandCategory.GAME,
            logger=self.logger,
            is_script=True,
        )
        self.assertIs(result, self.pipeline_command)

    def test_wrap_applies_in_script_context_when_enabled(self):
        wrapper = CommandWrapper(
            wrapper=lambda cmd, _: Command(["wrapped", cmd]),
            applies_for=[CommandCategory.GAME],
            use_in_script=True,
        )
        result = wrapper.wrap(
            self.pipeline_command,
            None,
            command_category=CommandCategory.GAME,
            logger=self.logger,
            is_script=True,
        )
        self.assertEqual(result.get_full_command(), "wrapped game.exe")

    def test_wrap_passes_parameter_through_to_wrapper_callable(self):
        received: list[object] = []

        def wrapper_fn(cmd: Command, parameter: object) -> Command:
            received.append(parameter)
            return cmd

        wrapper = CommandWrapper(wrapper=wrapper_fn)
        sentinel = object()
        _ = wrapper.wrap(
            self.pipeline_command,
            sentinel,
            command_category=CommandCategory.GAME,
            logger=self.logger,
        )
        self.assertEqual(received, [sentinel])

    def test_from_command_str_wraps_by_prepending_command(self):
        wrapper = CommandWrapper.from_command_str("gamemoderun")
        result = wrapper.wrap(
            self.pipeline_command,
            None,
            command_category=CommandCategory.GAME,
            logger=self.logger,
        )
        self.assertEqual(result.get_full_command(), "gamemoderun game.exe")

    def test_from_command_passes_through_applies_for_and_use_in_script(self):
        wrapper = CommandWrapper.from_command(
            Command.from_string("gamemoderun"),
            applies_for=[CommandCategory.TRAINER],
            use_in_script=True,
        )
        self.assertEqual(wrapper.applies_for, [CommandCategory.TRAINER])
        self.assertTrue(wrapper.use_in_script)


if __name__ == "__main__":
    _ = unittest.main()
