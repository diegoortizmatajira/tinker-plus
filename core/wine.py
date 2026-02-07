"""Module for managing Wine settings"""

import logging
from typing import final

from model import Command, RuntimeConfiguration

from .configuration_property import ListItem
from .process_runner import ProcessRunner

WIN_VERSIONS = {
    "winxp": "Windows XP",
    "win7": "Windows 7",
    "win8": "Windows 8",
    "win10": "Windows 10",
    "win11": "Windows 11",
}


@final
class Wine:
    """
    Provides functionality to manage Wine settings
    """

    @staticmethod
    def get_windows_list_items(
        _runtime_configuration: RuntimeConfiguration, _logger: logging.Logger
    ) -> list[ListItem[str]]:
        """
        Generate a list of ListItem objects representing Windows versions.

        Returns:
            list[ListItem[str]]: A list of ListItem objects, where each item contains
            the version key and its corresponding human-readable name.
        """
        return [ListItem(version, name) for version, name in WIN_VERSIONS.items()]

    @staticmethod
    def get_win_version(
        runtime_configuration: RuntimeConfiguration, logger: logging.Logger
    ) -> str | None:
        """
        Retrieves the current Windows version set in the Wine environment.

        Args:
            runtime_configuration (RuntimeConfiguration): The runtime configuration for Wine.
            logger (logging.Logger): The logger instance for logging messages.

        Returns:
            str | None: The current Windows version identifier (e.g., 'winxp', 'win7'),
                         or None if it cannot be determined.
        """
        succeed, output = ProcessRunner.run_in_wine_prefix(
            Command("winecfg", "/v"), runtime_configuration, logger, True
        )
        if succeed and output:
            for line in output.splitlines():
                line = line.strip()
                for version, description in WIN_VERSIONS.items():
                    if line.startswith(version):
                        logger.info(
                            "Current Windows version in Wine is %s", description
                        )
                        return version
        logger.error("Failed to retrieve Windows version from winecfg.")
        return None

    @staticmethod
    def set_win_version(
        version: str,
        runtime_configuration: RuntimeConfiguration,
        logger: logging.Logger,
    ) -> None:
        """
        Sets the Windows version for the Wine environment.

        Args:
            version (str): The Windows version identifier (e.g., 'winxp', 'win7').
            runtime_configuration (RuntimeConfiguration): The runtime configuration for Wine.
            logger (logging.Logger): The logger instance for logging messages.

        Raises:
            ValueError: If the provided Windows version is unsupported.
            RuntimeError: If the Wine configuration command fails.
        """
        description = WIN_VERSIONS.get(version)
        if description is None:
            logger.error("Unsupported Windows version: %s", version)
            raise ValueError(f"Unsupported Windows version: {version}")
        succeed = ProcessRunner.run_in_wine_prefix(
            Command("winecfg", f"/v {version}"),
            runtime_configuration,
            logger,
        )
        if succeed:
            logger.info("%s mode set successfully.", description)
        else:
            logger.error("%s mode setting failed.", description)
            raise RuntimeError("Winecfg failed")
