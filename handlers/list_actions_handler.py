"""Module for handling the 'list-actions' command."""

import logging
from typing import Any, override
from handlers.base_handler import BaseHandler

LIST_ACTIONS_COMMAND = "list-actions"


class ListActionsHandler(BaseHandler):
    """Handler for the 'list-actions' command.

    This handler is responsible for registering and executing the 'list-actions'
    command, which lists all available actions in the system along with their
    aliases and descriptions.
    """

    def __init__(
        self,
        subparser: Any,  # pyright: ignore[reportExplicitAny, reportAny]
        handlers: dict[str, BaseHandler],
    ) -> None:
        handlers[LIST_ACTIONS_COMMAND] = self
        subparser.add_parser(  # pyright: ignore[reportAny]
            LIST_ACTIONS_COMMAND, help="List available actions"
        )

    @override
    def handle(self, _args: object, logger: logging.Logger):
        logger.info("Listing available actions...")
        runtime_provider = self.get_runtime_provider([], True)
        actions = runtime_provider.get_available_actions()
        logger.info("Available Actions: %s", [action.name for action in actions])
        print("Available Actions:\n")
        for action in actions:
            print(f"  {action.alias:<30} {action.description}")
