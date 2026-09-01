"""Module for handling the 'execute' action command."""

import logging
from typing import Any, override
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
        subparser: Any,  # pyright: ignore[reportExplicitAny, reportAny]
        handlers: dict[str, BaseHandler],
    ) -> None:
        handlers[EXECUTE_ACTION_COMMAND] = self
        execute_parser: Any = subparser.add_parser(  # pyright: ignore[reportExplicitAny, reportAny]
            EXECUTE_ACTION_COMMAND, help="Execute a specified action"
        )
        execute_parser.add_argument(  # pyright: ignore[reportAny]
            "--dry", action="store_true", help="Run in DRY mode"
        )
        execute_parser.add_argument(  # pyright: ignore[reportAny]
            "action_alias", type=str, help="The alias of the action to execute"
        )

    @override
    def handle(self, args: object, logger: logging.Logger):
        """Looks up the action by alias and runs it via the runtime pipeline,
        logging an error if no action with that alias is found."""
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
