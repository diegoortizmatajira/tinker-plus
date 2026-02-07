"""Manages the collection of game configurations."""

from model import GameInfo

from .config_storage import ConfigStorage
from .log_storage import LogFactory


class GamesManager:
    """Manages the collection of games' configurations and their lifecycle.

    This class utilizes `GameInfo` to keep track of game configurations,
    initializes logs for debugging, and facilitates the retrieval of
    game configuration files.
    """

    def __init__(self, config_storage: ConfigStorage):
        self.__logger = LogFactory.singleton().get_logger(self.__class__.__name__)
        self.__games: list[GameInfo] = []
        self.__config_storage = config_storage
        self.get_configured_games()

    def get_configured_games(self):
        """Retrieve and initialize the list of configured games.

        This function fetches game configuration files, converts them into
        `GameInfo` objects, filters out invalid entries, and sorts the
        resulting list of games by their names in a case-insensitive manner.
        """
        self.__logger.info("Retrieving configured games...")
        files = self.__config_storage.get_game_configuration_files()
        self.__logger.debug("Found %d game configuration files.", len(files))
        # Get the game_id from file names and create GameInfo objects
        self.__games = [
            item
            for item in [
                GameInfo.from_cache(file.stem, self.__logger) for file in files
            ]
            if item is not None
        ]
        self.__logger.info("Loaded %d valid game configurations.", len(self.__games))
        self.__games.sort(key=lambda game: game.name.lower())

    def get_games(self) -> list[GameInfo]:
        """Get the list of configured games.

        Returns:
            list[GameInfo]: A list of configured games.
        """
        return self.__games
