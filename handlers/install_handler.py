"""Module to handle installation as a Steam compatibility tool."""

import logging
import os
from pathlib import Path
import shutil
from typing import Any, override
from defaults import (
    ACTUAL_TPLUS_LOCATION,
    TPLUS_BIN_LOCATION,
    TPLUS_COMPATIBILITY_TOOL_DIR,
)
from file_system import FileSystem
from handlers.base_handler import BaseHandler

INSTALL_COMMAND = "install"


class InstallHandler(BaseHandler):
    """
    Handles the installation process for the application as a Steam compatibility tool.

    This class defines the `install` command, prepares the necessary resources,
    and executes the installation process. It ensures that the application is set up
    correctly as a Steam compatibility tool by creating symbolic links, copying required
    files, and setting up the tool's directory structure.
    """

    def __init__(
        self,
        subparser: Any,  # pyright: ignore[reportExplicitAny, reportAny]
        handlers: dict[str, BaseHandler],
    ) -> None:
        handlers[INSTALL_COMMAND] = self
        subparser.add_parser(  # pyright: ignore[reportAny]
            INSTALL_COMMAND, help="Install as Steam compatibility tool"
        )

    @override
    def handle(
        self,
        _args: object,
        logger: logging.Logger,
    ) -> None:
        """
        Installs Tinker-Plus as a Steam compatibility tool.

        Symlinks the `tplus` launcher into the configured bin location, recreates
        the compatibility tool directory, and copies/symlinks the manifest and
        launcher files into it so Steam can discover and launch it.
        """
        logger.info(
            "Creating symbolic link for Tinker-Plus (tplus) in '%s'", TPLUS_BIN_LOCATION
        )
        tinker_plus_sh_path = os.path.join(ACTUAL_TPLUS_LOCATION, "tinker-plus.sh")

        FileSystem.create_symbolic_link(tinker_plus_sh_path, TPLUS_BIN_LOCATION, logger)
        # Check if the compatibility tool directory exists, and remove it if it does.
        compat_path = Path(TPLUS_COMPATIBILITY_TOOL_DIR)
        if compat_path.exists() and compat_path.is_dir():
            logger.info(
                "Removing existing compatibility tool directory at '%s'",
                TPLUS_COMPATIBILITY_TOOL_DIR,
            )
            shutil.rmtree(compat_path)

        logger.info(
            "Installing as Steam compatibility tool at '%s'",
            compat_path,
        )
        compat_path.mkdir(parents=True, exist_ok=True)
        files_to_copy = {
            "toolmanifest.vdf": "./resources/toolmanifest.vdf",
            "compatibilitytool.vdf": "./resources/compatibilitytool.vdf",
        }
        for target, source in files_to_copy.items():
            target_path = compat_path.joinpath(target)
            # Copy the file
            _ = shutil.copy(source, target_path)
        files_to_link = {
            "tplus": tinker_plus_sh_path,
        }

        for link_name, target in files_to_link.items():
            link_path = compat_path.joinpath(link_name)
            FileSystem.create_symbolic_link(target, str(link_path), logger)
        logger.info("Installation as Steam compatibility tool completed.")
