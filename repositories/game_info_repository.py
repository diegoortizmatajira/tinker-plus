"""Module: game_info_repository.py"""

from dataclasses import asdict
import os
import json
import logging
from typing import cast
from model import GameInfo

from defaults import GLOBAL_GAME_INFO_CACHE_FILE


class GameInfoRepository:
    """
    The GameInfoRepository class manages the caching of game information. It
    provides methods to retrieve and save game information in a cache file. The
    cache is stored as a class variable and is loaded from the file when first
    accessed. The class also handles exceptions that may occur during file
    operations, ensuring that the application can continue to function even if
    the cache cannot be loaded or saved.
    """

    _cache: dict[str, "GameInfo"] | None = None

    @classmethod
    def get_cache(
        cls, logger: logging.Logger, dry_run: bool = False
    ) -> dict[str, "GameInfo"]:
        """
        Retrieves the game information cache, loading it from the cache file if
        it is not already in memory.

        Args:
            logger (logging.Logger): The logger instance used for logging
                messages during the cache retrieval process.
            dry_run (bool): If True, an empty cache is not persisted to disk when
                the cache file doesn't exist yet.

        Returns:
            dict[str, GameInfo]: The game information cache as a dictionary
            with game IDs as keys and GameInfo objects as values. If the cache
            file does not exist or fails to load, an empty dictionary is
            returned.
        """
        if cls._cache is not None:
            return cls._cache
        try:
            if not os.path.exists(GLOBAL_GAME_INFO_CACHE_FILE):
                logger.info("Game info cache file does not exist. Creating a new one.")
                cls.save_cache({}, logger, dry_run)
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
    def save_cache(
        cls,
        cache: dict[str, "GameInfo"],
        logger: logging.Logger,
        dry_run: bool = False,
    ):
        """
        Saves the given game information cache to a file.

        Args:
            cache (dict[str, GameInfo]): The cache to save, where the keys are game IDs
                                         and values are GameInfo objects.
            logger (logging.Logger): The logger instance to log messages related to saving cache.
            dry_run (bool): If True, logs the intended write instead of performing it.
        """
        cls._cache = cache
        if dry_run:
            logger.info(
                "Dry run: would save game info cache to: %s",
                GLOBAL_GAME_INFO_CACHE_FILE,
            )
            return
        try:
            raw_cache = {game_id: asdict(info) for game_id, info in cache.items()}
            with open(GLOBAL_GAME_INFO_CACHE_FILE, "w", encoding="utf-8") as cache_file:
                json.dump(raw_cache, cache_file, indent=4)
            logger.info("Game info cache saved successfully.")
        except (OSError, IOError) as e:
            logger.warning("Failed to save game info cache: %s", e)

    @classmethod
    def from_cache(
        cls, game_id: str, logger: logging.Logger, dry_run: bool = False
    ) -> "GameInfo | None":
        """
        Retrieves a GameInfo object from the cache using the given game ID.

        Args:
            game_id (str): The unique identifier for the game.
            logger (logging.Logger): The logger instance used for logging messages.
            dry_run (bool): If True, an empty cache is not persisted to disk when
                the cache file doesn't exist yet.

        Returns:
            GameInfo | None: The GameInfo object if found in the cache, otherwise None.
        """
        cache = cls.get_cache(logger, dry_run)
        return cache.get(game_id)

    @classmethod
    def put_in_cache(
        cls, item: GameInfo, logger: logging.Logger, dry_run: bool = False
    ):
        """
        Adds the current GameInfo object to the cache and saves the updated cache.

        Args:
            item (GameInfo): The game info object to add to the cache.
            logger (logging.Logger): The logger instance used for logging messages
                                     during the cache update process.
            dry_run (bool): If True, the updated cache is not saved to disk.
        """
        cache = cls.get_cache(logger, dry_run)
        cache[item.game_id] = item
        cls.save_cache(cache, logger, dry_run)
        logger.info("Game info for '%s' added to cache.", item.name)
