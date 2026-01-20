"""
Main entry point for the Tinker-Plus application.
"""

import argparse
import logging
import os
import sys
from typing import Any


from core import LogFactory
from handlers.base_handler import BaseHandler
from handlers.execute_action_handler import ExecuteActionHandler
from handlers.generate_documentation_handler import GenerateDocumentationHandler
from handlers.install_handler import InstallHandler
from handlers.list_actions_handler import ListActionsHandler
from handlers.list_games_handler import ListGamesHandler
from handlers.run_handler import RunHandler
from handlers.validate_games_config import ValidateGamesConfig


def main():
    """
    The main entry point for the Tinker-Plus application.

    This function sets up the argument parser for the application, initializes
    command handlers, and processes commands supplied by the user. It also
    manages logging configuration based on the debug mode and handles the
    application's lifecycle.

    Raises:
        SystemExit: If no command is provided by the user.
    """
    # print the full command line for debugging purposes
    print("Command line:", " ".join(sys.argv))
    parser = argparse.ArgumentParser(description="Tinker-Plus Application")
    _ = parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    subparsers: Any = parser.add_subparsers(  # pyright: ignore[reportExplicitAny]
        title="Commands", dest="command"
    )
    subparsers.required = True

    # Initialize command handlers (They register themselves)
    command_handlers: dict[str, BaseHandler] = {}
    _ = RunHandler(subparsers, command_handlers)
    _ = InstallHandler(subparsers, command_handlers)
    _ = GenerateDocumentationHandler(subparsers, command_handlers)
    _ = ListActionsHandler(subparsers, command_handlers)
    _ = ExecuteActionHandler(subparsers, command_handlers)
    _ = ListGamesHandler(subparsers, command_handlers)
    _ = ValidateGamesConfig(subparsers, command_handlers)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    handler = command_handlers.get(args.command)  # pyright: ignore[reportAny]

    debug_mode = getattr(args, "debug", False)

    # Set Steam Game ID from environment variable if available
    game_id = os.getenv("SteamGameId") or "unknown"

    factory = LogFactory.initialize(
        game_id,
        console_level=logging.DEBUG if debug_mode else logging.ERROR,
        file_level=logging.DEBUG if debug_mode else logging.INFO,
    )
    logger = factory.get_logger("TinkerPlus")
    logger.info("Starting Tinker-Plus application...")
    result_code = 0
    if handler:
        try:
            handler.handle(args, logger)
        except RuntimeError as e:
            logger.error("Runtime error occurred: %s", str(e))
            result_code = 1
    else:
        logger.error("No valid command handler found.")
    logger.info("Tinker-Plus application finished.")
    sys.exit(result_code)


if __name__ == "__main__":
    main()
