"""Module to handle the 'run' command for executing the main application process."""

import argparse
import logging
from typing import override

from features.gui_options import CURRENT_GUI_OPTIONS
from gui.main_form import MainForm
from handlers.base_handler import BaseHandler

RUN_COMMAND = "run"


class RunHandler(BaseHandler):
    """
    Handles the 'run' command which initiates the main application process.
    This handler supports various operational modes such as GUI, dry run (no game
    launch), and trainer execution. It also facilitates execution of the specified
    game command with its parameters.
    """

    def __init__(
        self,
        subparser: argparse._SubParsersAction,
        handlers: dict[str, BaseHandler],
    ) -> None:
        handlers[RUN_COMMAND] = self
        run_parser: argparse.ArgumentParser = subparser.add_parser(
            RUN_COMMAND,
            help="Run the main application process.",
            description="This command starts the main application process"
            " with the specified configurations.",
        )
        run_parser.add_argument(
            "--gui",
            action="store_true",
            help="Run in GUI mode",
        )
        run_parser.add_argument(
            "--nogui",
            action="store_true",
            help="Run in GUI mode",
        )
        run_parser.add_argument(
            "--dry", action="store_true", help="Run in DRY mode (no game launch)"
        )
        run_parser.add_argument(
            "--trainer", action="store_true", help="Run with trainer"
        )
        run_parser.add_argument(
            "game_command",
            nargs="+",  # Accepts any number of arguments as a list
            help=(
                "The command to launch the game followed by its parameters"
                " (e.g., executable + arguments)"
            ),
        )

    @override
    def handle(
        self,
        args: argparse.Namespace,
        logger: logging.Logger,
    ) -> None:
        dry_run = getattr(args, "dry", False)
        execute_trainer = getattr(args, "trainer", True)
        game_command = getattr(args, "game_command", [])

        try:
            runtime = self.get_runtime_provider(game_command, dry_run)
            runtime.build_configuration(True)
            if runtime.runtime_configuration is None:
                raise RuntimeError("Failed to build runtime configuration.")
            runtime.runtime_configuration.execute_trainers = execute_trainer
            # Uses the read setting for GUI if not explicitly provided
            use_gui = not getattr(args, "nogui") and (
                getattr(args, "gui") or CURRENT_GUI_OPTIONS.use_ui
            )
            if use_gui:
                logger.info("💡 Using Graphical User Interface Display")
                main_form = MainForm(runtime, CURRENT_GUI_OPTIONS.autorun_timeout)
                main_form.show()
            else:
                runtime.run()

        except RuntimeError as e:
            logger.error("An error occurred during runtime execution. %s", e)
