"""
Main entry point for the Tinker-Plus application.
"""

import argparse
import logging
import os
import sys


from core import LogFactory
from handlers.base_handler import BaseHandler
from handlers.generate_documentation_handler import GenerateDocumentationHandler
from handlers.install_handler import InstallHandler
from handlers.run_handler import RunHandler


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
    parser = argparse.ArgumentParser(description="Tinker-Plus Application")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    subparsers.required = True

    # Initialize command handlers (They register themselves)
    command_handlers: dict[str, BaseHandler] = {}
    RunHandler(subparsers, command_handlers)
    InstallHandler(subparsers, command_handlers)
    GenerateDocumentationHandler(subparsers, command_handlers)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    handler = command_handlers.get(args.command)

    debug_mode = getattr(args, "debug", False)

    # Set Steam Game ID from environment variable if available
    game_id = os.getenv("SteamGameId") or "unknown"

    factory = LogFactory.initialize(
        game_id, logging.DEBUG if debug_mode else logging.INFO, True
    )
    logger = factory.get_logger("TinkerPlus")
    logger.info("Starting Tinker-Plus application...")
    if handler:
        handler.handle(args, logger)
    else:
        logger.error("No valid command handler found.")
    logger.info("Tinker-Plus application finished.")


if __name__ == "__main__":
    main()
