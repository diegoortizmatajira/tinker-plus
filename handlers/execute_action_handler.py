"""Module for handling the 'execute' action command."""

import argparse
import logging
from typing import override
from handlers.base_handler import BaseHandler

EXECUTE_ACTION_COMMAND = "execute"


class ExecuteActionHandler(BaseHandler):
    """
    Handler for the 'execute' action command.

    This class initializes the command-line interface for executing a specific action
    and provides the implementation for handling the execution logic.
    """

    def __init__(
        self,
        subparser: argparse._SubParsersAction,
        handlers: dict[str, BaseHandler],
    ) -> None:
        handlers[EXECUTE_ACTION_COMMAND] = self
        execute_parser = subparser.add_parser(
            EXECUTE_ACTION_COMMAND, help="Execute a specified action"
        )
        execute_parser.add_argument(
            "--dry", action="store_true", help="Run in DRY mode"
        )
        execute_parser.add_argument(
            "action_alias", type=str, help="The alias of the action to execute"
        )

    @override
    def handle(self, args, logger: logging.Logger):
        selected_action = getattr(args, "action_alias", "")
        dry_run = getattr(args, "dry", False)
        runtime_provider = self.get_runtime_provider([], dry_run)
        actions = runtime_provider.get_available_actions()
        found_actions = [
            action for action in actions if action.alias == selected_action
        ]
        if len(found_actions) == 0:
            logger.error("Action with alias '%s' not found.", selected_action)
            print(f"Action with alias '{selected_action}' not found.")
            return

        runtime_provider.build_configuration()
        runtime_provider.run_action(found_actions[0])
