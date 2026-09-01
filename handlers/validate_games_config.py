"""Module for handling the 'validate-games' command."""

import logging
from typing import Any, override
from core import ConfigStorage, GamesManager
from handlers.base_handler import BaseHandler

VALIDATE_GAMES_COMMAND = "validate-games"


class ValidateGamesConfig(BaseHandler):
    """
    Handles the "validate-games" command, which checks every configured game's
    stored configuration for unexpected keys against the currently registered
    feature providers.
    """

    def __init__(
        self,
        subparser: Any,  # pyright: ignore[reportExplicitAny, reportAny]
        handlers: dict[str, BaseHandler],
    ) -> None:
        handlers[VALIDATE_GAMES_COMMAND] = self
        subparser.add_parser(VALIDATE_GAMES_COMMAND, help="Validate configured games")  # pyright: ignore[reportAny]

    @override
    def handle(self, _args: object, logger: logging.Logger):
        """Validates every configured game's stored configuration and prints
        an OK/INVALID status line (with issue details) for each one."""
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
