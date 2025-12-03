import argparse
import logging
from typing import override
from handlers.base_handler import BaseHandler

EXECUTE_ACTION_COMMAND = "execute"


class ExecuteActionHandler(BaseHandler):
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
            "action_alias", type=str, help="The alias of the action to execute"
        )

    @override
    def handle(self, _args, logger: logging.Logger):
        runtime_provider = self.get_runtime_provider([], True)
        actions = runtime_provider.get_available_actions()
        selected_action = getattr(_args, "action_alias", "")
        found_actions = [
            action for action in actions if action.alias == selected_action
        ]
        if len(found_actions) == 0:
            logger.error("Action with alias '%s' not found.", selected_action)
            print(f"Action with alias '{selected_action}' not found.")
            return

        runtime_provider.build_configuration()
        runtime_provider.run_action(found_actions[0])
