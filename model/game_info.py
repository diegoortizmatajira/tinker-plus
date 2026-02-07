"""Module for managing game information and caching."""

from dataclasses import asdict, dataclass
import logging
import json
import os
from typing import ClassVar, cast

from core.defaults import GLOBAL_GAME_INFO_CACHE_FILE


@dataclass
class GameInfo:
    """
    Represents information about a game, including its unique identifier
    and name. This class also provides methods for managing and accessing
    a cache of game information.

    Attributes:
        game_id (str): The unique identifier for the game.
        name (str): The name of the game.
    """

    game_id: str
    name: str

    _cache: ClassVar[dict[str, "GameInfo"] | None] = None

    @classmethod
    def get_cache(cls, logger: logging.Logger) -> dict[str, "GameInfo"]:
        """
        Retrieves the game information cache, loading it from the cache file if
        it is not already in memory.

        Args: logger (logging.Logger): The logger instance used for logging
        messages during the cache retrieval process.

        Returns: dict[str, GameInfo]: The game information cache as a
        dictionary with game IDs as keys and GameInfo objects as values. If the
        cache file does not exist or fails to load, an empty dictionary is
        returned.
        """
        if cls._cache is not None:
            return cls._cache
        try:
            if not os.path.exists(GLOBAL_GAME_INFO_CACHE_FILE):
                logger.info("Game info cache file does not exist. Creating a new one.")
                GameInfo.save_cache({}, logger)
                return {}

            with open(GLOBAL_GAME_INFO_CACHE_FILE, "r", encoding="utf-8") as cache_file:
                raw_cache: dict[str, dict[str, str]] = cast(
                    dict[str, dict[str, str]], json.load(cache_file)
                )
                cache = {
                    game_id: GameInfo(**info) for game_id, info in raw_cache.items()
                }
                cls._cache = cache
                return cache
        except (OSError, IOError, json.JSONDecodeError) as e:
            logger.warning("Failed to load game info cache: %s", e)
            return {}

    @classmethod
    def save_cache(cls, cache: dict[str, "GameInfo"], logger: logging.Logger):
        """
        Saves the given game information cache to a file.

        Args:
            cache (dict[str, GameInfo]): The cache to save, where the keys are game IDs
                                         and values are GameInfo objects.
            logger (logging.Logger): The logger instance to log messages related to saving cache.

        Raises:
            Exception: If there's an error during the saving process, a warning is logged.
        """
        cls._cache = cache
        try:
            raw_cache = {game_id: asdict(info) for game_id, info in cache.items()}
            with open(GLOBAL_GAME_INFO_CACHE_FILE, "w", encoding="utf-8") as cache_file:
                json.dump(raw_cache, cache_file, indent=4)
            logger.info("Game info cache saved successfully.")
        except (OSError, IOError) as e:
            logger.warning("Failed to save game info cache: %s", e)

    @staticmethod
    def empty() -> "GameInfo":
        """
        Creates an empty GameInfo object with default values.

        Returns:
            GameInfo: An empty GameInfo object with default values.
        """
        return GameInfo(game_id="unknown", name="unknown")

    @staticmethod
    def from_cache(game_id: str, logger: logging.Logger) -> "GameInfo | None":
        """
        Retrieves a GameInfo object from the cache using the given game ID.

        Args:
            game_id (str): The unique identifier for the game.

        Returns:
            Optional[GameInfo]: The GameInfo object if found in the cache, otherwise None.
        """
        cache = GameInfo.get_cache(logger)
        return cache.get(game_id)

    def put_in_cache(self, logger: logging.Logger):
        """
        Adds the current GameInfo object to the cache and saves the updated cache.

        Args:
            logger (logging.Logger): The logger instance used for logging messages
                                     during the cache update process.
        """
        cache = GameInfo.get_cache(logger)
        cache[self.game_id] = self
        GameInfo.save_cache(cache, logger)
        logger.info("Game info for '%s' added to cache.", self.name)
