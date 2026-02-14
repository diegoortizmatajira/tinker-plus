"""Module for managing compatibility tool information and caching."""

from dataclasses import asdict, dataclass
import json
import logging
import os
from pathlib import Path
from typing import ClassVar, cast

from defaults import LOG_SEARCHING, GLOBAL_COMPAT_TOOL_CACHE_FILE
from file_system import FileSystem

from .runtime_configuration import RuntimeConfiguration


@dataclass
class CompatToolInfo:
    """
    This class represents compatibility tool information and manages a cache for these tools.

    Attributes:
        name (str): The name of the compatibility tool.
        dir (str): The directory where the compatibility tool is located.
        _cache (ClassVar[dict[str, "CompatToolInfo"]] | None): A class-level cache
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

