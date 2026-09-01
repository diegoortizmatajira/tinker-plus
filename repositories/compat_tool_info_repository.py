"""Module: compat_tool_info_repository.py"""

import json
import logging
import os
from dataclasses import asdict
from pathlib import Path
from typing import cast

from core.steam.defaults import (
    DEFAULT_STEAM_COMMON_FOLDER,
    DEFAULT_STEAM_COMPATIBILITY_TOOLS_FOLDER,
    DEFAULT_STEAM_FOLDER,
)
from defaults import GLOBAL_COMPAT_TOOL_CACHE_FILE, LOG_SEARCHING
from file_system import FileSystem
from model import CompatToolInfo, RuntimeConfiguration


class CompatToolInfoRepository:
    """
    The CompatToolInfoRepository class is responsible for managing
    compatibility tool information and caching it for efficient retrieval. It
    provides methods to retrieve, save, and update the cache of compatibility
    tools, as well as to scan directories for available tools and populate the
    cache accordingly.
    """

    _cache: dict[str, CompatToolInfo] | None = None

    @classmethod
    def get_cache(
        cls, logger: logging.Logger, dry_run: bool = False
    ) -> dict[str, CompatToolInfo]:
        """
        Retrieve the cached compatibility tool information.

        This method attempts to load the cache from a predefined global file. If the
        cache file does not exist, a new cache is created and saved to the file. If
        any exception occurs during the loading process, an empty cache is returned.

        Args:
            logger (logging.Logger): The logger instance used for logging messages.
            dry_run (bool): If True, the function will simulate changes without saving.

        Returns:
            dict[str, CompatToolInfo]: A dictionary containing the cached compatibility
            tool information, where keys are tool names and values are CompatToolInfo
            objects.
        """
        if cls._cache is not None:
            return cls._cache

        try:
            if not os.path.exists(GLOBAL_COMPAT_TOOL_CACHE_FILE):
                logger.info(
                    "Compatibility tool info cache file does not exist. Creating a new one."
                )
                cls.save_cache({}, logger, dry_run)
                return {}

            with open(
                GLOBAL_COMPAT_TOOL_CACHE_FILE, "r", encoding="utf-8"
            ) as cache_file:
                raw_cache: dict[str, dict[str, str]] = cast(
                    dict[str, dict[str, str]], json.load(cache_file)
                )
                cache: dict[str, CompatToolInfo] = {
                    name: CompatToolInfo(**info) for name, info in raw_cache.items()
                }
                cls._cache = cache
                return cache
        except (OSError, IOError, json.JSONDecodeError) as e:
            logger.warning("Failed to load compatibility tool info cache: %s", e)
            return {}

    @classmethod
    def save_cache(
        cls,
        cache: dict[str, CompatToolInfo],
        logger: logging.Logger,
        dry_run: bool,
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
            dry_run (bool): If True, skips writing the cache file to disk.
        """
        cls._cache = cache
        raw_cache = {name: asdict(info) for name, info in cache.items()}
        FileSystem.dump_as_json(
            raw_cache, GLOBAL_COMPAT_TOOL_CACHE_FILE, dry_run, logger
        )
        logger.info("Compatibility tool info cache saved successfully.")

    @classmethod
    def from_cache(
        cls, name: str, logger: logging.Logger, dry_run: bool = False
    ) -> CompatToolInfo | None:
        """
        Retrieve a CompatToolInfo object from the cache by its name.

        This method looks up the compatibility tool information in the cache using
        the provided tool name. If the tool is not found in the cache, None is returned.

        Args:
            name (str): The name of the compatibility tool to retrieve.
            logger (logging.Logger): The logger instance used for logging messages.
            dry_run (bool): If True, an empty cache is not persisted to disk when
                the cache file doesn't exist yet.

        Returns:
            CompatToolInfo | None: The CompatToolInfo object corresponding to the
            given name if it exists in the cache, otherwise None.
        """
        cache = cls.get_cache(logger, dry_run)
        return cache.get(name)

    @classmethod
    def scan_and_populate_cache(
        cls,
        logger: logging.Logger,
        configuration: RuntimeConfiguration,
        dry_run: bool = False,
    ) -> dict[str, CompatToolInfo]:
        """
        Scan the compatibility tools directory for available tools.

        This method scans the predefined compatibility tools directory for available
        compatibility tools and returns a list of CompatToolInfo objects representing
        each found tool.

        Args:
            logger (logging.Logger): The logger instance used for logging messages.
            configuration (RuntimeConfiguration): Runtime configuration providing the
                Steam base folder and selected compatibility tools path to scan.
            dry_run (bool): If True, the refreshed cache is not saved to disk.
        Returns:
            dict[str, CompatToolInfo]: The refreshed cache, keyed by tool name.
        """
        compat_dirs = [
            DEFAULT_STEAM_COMMON_FOLDER.format(
                configuration.steam_environment_data.steam_base_folder
                or DEFAULT_STEAM_FOLDER
            ),
            DEFAULT_STEAM_COMPATIBILITY_TOOLS_FOLDER.format(
                configuration.steam_environment_data.steam_base_folder
                or DEFAULT_STEAM_FOLDER
            ),
        ]
        if configuration.steam_compatibility_tools_path:
            current_path = Path(configuration.steam_compatibility_tools_path).as_posix()
            if current_path not in compat_dirs:
                compat_dirs.append(current_path)

        initial_cache = cls.get_cache(logger).copy()
        # Include directories from the existing cache
        for _, value in initial_cache.items():
            cache_value_path = Path(value.dir).as_posix()
            if cache_value_path not in compat_dirs:
                compat_dirs.append(cache_value_path)

        seen_directories: set[str] = set()
        new_cache: dict[str, CompatToolInfo] = {}
        for compat_dir in compat_dirs:
            logger.info(
                LOG_SEARCHING.format("Searching for proton versions in: %s"), compat_dir
            )
            compat_dir_path = Path(compat_dir)
            if compat_dir_path.exists() and compat_dir_path.is_dir():
                folders = compat_dir_path.glob("*Proton*")
                for folder in folders:
                    if folder.is_dir() and folder.name not in seen_directories:
                        logger.debug("Found proton version: %s", folder.name)
                        new_cache[folder.name] = CompatToolInfo(
                            folder.name, folder.parent.as_posix()
                        )
                        seen_directories.add(folder.name)
        cls.save_cache(new_cache, logger, dry_run)
        return cls.get_cache(logger)

    @classmethod
    def put_in_cache(
        cls, item: CompatToolInfo, logger: logging.Logger, dry_run: bool = False
    ):
        """
        Add the current CompatToolInfo object to the cache.

        This method updates the compatibility tool info cache with the current
        object and ensures the updated cache is saved to the predefined global
        file. A log message is generated to indicate the addition.

        Args:
            item (CompatToolInfo): The compatibility tool info to add to the cache.
            logger (logging.Logger): The logger instance used for logging messages.
            dry_run (bool): If True, the updated cache is not saved to disk.
        """
        cache = cls.get_cache(logger)
        cache[item.name] = item
        cls.save_cache(cache, logger, dry_run)
        logger.info("Compatibility tool info for '%s' added to cache.", item.name)
