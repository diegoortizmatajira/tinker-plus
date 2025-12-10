import argparse
import logging
from typing import override
from core.config_storage import ConfigStorage
from core.games_manager import GamesManager
from handlers.base_handler import BaseHandler

VALIDATE_GAMES_COMMAND = "validate-games"


class ValidateGamesConfig(BaseHandler):
    def __init__(
        self,
        subparser: argparse._SubParsersAction,
        handlers: dict[str, BaseHandler],
    ) -> None:
        handlers[VALIDATE_GAMES_COMMAND] = self
        subparser.add_parser(VALIDATE_GAMES_COMMAND, help="Validate configured games")

    @override
    def handle(self, _args, logger: logging.Logger):
        logger.info("Listing configured games...")
        config_storage = ConfigStorage()
        manager = GamesManager(config_storage)
        games = manager.get_games()
        runtime_provider = self.get_runtime_provider([], True)
        print("Game Config Status:\n")
        for game in games:
            issues = config_storage.validate_config(game, runtime_provider.features)
            ok = len(issues) == 0
            print(f"  {'[OK]' if ok else '[INVALID]':<12} {game.name}")
            if not ok:
                for issue in issues:
                    print(f"    >> {issue}")
