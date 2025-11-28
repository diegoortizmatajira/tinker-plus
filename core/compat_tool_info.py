"""Module for managing compatibility tool information and caching."""

from dataclasses import asdict, dataclass
import json
import logging
import os
from typing import ClassVar, Optional

from core.defaults import GLOBAL_COMPAT_TOOL_CACHE_FILE


@dataclass
class CompatToolInfo:
    """
    This class represents compatibility tool information and manages a cache for these tools.

    Attributes:
        name (str): The name of the compatibility tool.
        dir (str): The directory where the compatibility tool is located.
        _cache (ClassVar[Optional[dict[str, "CompatToolInfo"]]]): A class-level cache
            to store compatibility tool information.

    Methods:
        get_cache(cls, logger): Retrieve the cached compatibility tool information.
        save_cache(cls, cache, logger): Save the compatibility tool information cache to a file.
        empty(): Create and return an empty CompatToolInfo object.
        from_cache(name, logger): Retrieve a CompatToolInfo object from the cache by its name.
        put_in_cache(self, logger): Add the current CompatToolInfo object to the cache.
    """

    name: str
    dir: str
    _cache: ClassVar[Optional[dict[str, "CompatToolInfo"]]] = None

    @classmethod
    def get_cache(
        cls, logger: Optional[logging.Logger] = None
    ) -> dict[str, "CompatToolInfo"]:
        """
        Retrieve the cached compatibility tool information.

        This method attempts to load the cache from a predefined global file. If the
        cache file does not exist, a new cache is created and saved to the file. If
        any exception occurs during the loading process, an empty cache is returned.

        Args:
            logger (logging.Logger): The logger instance used for logging messages.

        Returns:
            dict[str, CompatToolInfo]: A dictionary containing the cached compatibility
            tool information, where keys are tool names and values are CompatToolInfo
            objects.
        """
        if cls._cache is not None:
            return cls._cache
        try:
            if not os.path.exists(GLOBAL_COMPAT_TOOL_CACHE_FILE):
                if logger:
                    logger.info(
                        "Compatibility tool info cache file does not exist. Creating a new one."
                    )
                CompatToolInfo.save_cache({}, logger)
                return {}

            with open(
                GLOBAL_COMPAT_TOOL_CACHE_FILE, "r", encoding="utf-8"
            ) as cache_file:
                raw_cache = json.load(cache_file)
                cache = {
                    name: CompatToolInfo(**info) for name, info in raw_cache.items()
                }
                cls._cache = cache
                return cache
        except Exception as e:
            if logger:
                logger.warning("Failed to load compatibility tool info cache: %s", e)
            return {}

    @classmethod
    def save_cache(
        cls, cache: dict[str, "CompatToolInfo"], logger: Optional[logging.Logger] = None
    ):
        """
        Save the compatibility tool information cache to a file.

        This method updates and saves the given cache to a predefined global file. If
        there is an error during the saving process, an appropriate warning is logged.

        Args:
            cache (dict[str, CompatToolInfo]): A dictionary containing the compatibility
            tool information to be saved, where keys are tool names and values are
            CompatToolInfo objects.
            logger (logging.Logger): The logger instance used for logging messages.
        """
        cls._cache = cache
        try:
            raw_cache = {name: asdict(info) for name, info in cache.items()}
            with open(
                GLOBAL_COMPAT_TOOL_CACHE_FILE, "w", encoding="utf-8"
            ) as cache_file:
                json.dump(raw_cache, cache_file, indent=4)
            if logger:
                logger.info("Compatibility tool info cache saved successfully.")
        except Exception as e:
            if logger:
                logger.warning("Failed to save compatibility tool info cache: %s", e)

    @staticmethod
    def empty() -> "CompatToolInfo":
        """
        Create and return an empty CompatToolInfo object.

        This static method creates a CompatToolInfo object with default values.
        It is primarily used as a placeholder or default value.

        Returns:
            CompatToolInfo: An instance of CompatToolInfo with "unknown" as the name
            and "." as the directory.
        """
        return CompatToolInfo(name="unknown", dir=".")

    @staticmethod
    def from_cache(name: str, logger: logging.Logger) -> Optional["CompatToolInfo"]:
        """
        Retrieve a CompatToolInfo object from the cache by its name.

        This method looks up the compatibility tool information in the cache using
        the provided tool name. If the tool is not found in the cache, None is returned.

        Args:
            name (str): The name of the compatibility tool to retrieve.
            logger (logging.Logger): The logger instance used for logging messages.

        Returns:
            Optional[CompatToolInfo]: The CompatToolInfo object corresponding to the
            given name if it exists in the cache, otherwise None.
        """
        cache = CompatToolInfo.get_cache(logger)
        return cache.get(name)

    def put_in_cache(self, logger: logging.Logger):
        """
        Add the current CompatToolInfo object to the cache.

        This method updates the compatibility tool info cache with the current
        object and ensures the updated cache is saved to the predefined global
        file. A log message is generated to indicate the addition.

        Args:
            logger (logging.Logger): The logger instance used for logging messages.
        """
        cache = CompatToolInfo.get_cache(logger)
        cache[self.name] = self
        CompatToolInfo.save_cache(cache, logger)
        logger.info("Compatibility tool info for '%s' added to cache.", self.name)
