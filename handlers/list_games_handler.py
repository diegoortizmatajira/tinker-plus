import argparse
import logging
from typing import override
from core.config_storage import ConfigStorage
from core.games_manager import GamesManager
from handlers.base_handler import BaseHandler

LIST_GAMES_COMMAND = "list-games"


class ListGamesHandler(BaseHandler):
    def __init__(
        self,
        subparser: argparse._SubParsersAction,
        handlers: dict[str, BaseHandler],
    ) -> None:
        handlers[LIST_GAMES_COMMAND] = self
        subparser.add_parser(LIST_GAMES_COMMAND, help="List configured games")

    @override
    def handle(self, _args, logger: logging.Logger):
        logger.info("Listing configured games...")
        manager = GamesManager(ConfigStorage())
        logger.info("Available Games: %s", [game.name for game in manager.get_games()])
        print("Available Games:\n")
        for game in manager.get_games():
            print(f"  {game.game_id:<30} {game.name}")
