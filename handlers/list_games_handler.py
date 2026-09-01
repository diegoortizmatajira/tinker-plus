"""Module for handling the 'list-games' command."""

import logging
from typing import Any, override
from core import ConfigStorage, GamesManager
from handlers.base_handler import BaseHandler

LIST_GAMES_COMMAND = "list-games"


class ListGamesHandler(BaseHandler):
    """
    Handles the "list-games" command to display a list of configured games.

    This class integrates with the command-line parser and provides the necessary
    functionality to handle and display configured games using the GamesManager.
    """

    def __init__(
        self,
        subparser: Any,  # pyright: ignore[reportExplicitAny, reportAny]
        handlers: dict[str, BaseHandler],
    ) -> None:
        handlers[LIST_GAMES_COMMAND] = self
        subparser.add_parser(  # pyright: ignore[reportAny]
            LIST_GAMES_COMMAND, help="List configured games"
        )

    @override
    def handle(self, _args: object, logger: logging.Logger):
        """Prints the game ID and name of every configured game."""
        logger.info("Listing configured games...")
        manager = GamesManager(ConfigStorage())
        logger.info("Available Games: %s", [game.name for game in manager.get_games()])
        print("Available Games:\n")
        for game in manager.get_games():
            print(f"  {game.game_id:<30} {game.name}")
