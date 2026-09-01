"""Module to handle installation as a Steam compatibility tool."""

import logging
import os
from pathlib import Path
import shutil
import stat
from typing import Any, override
from core.steam.defaults import (
    DEFAULT_STEAM_COMPATIBILITY_TOOLS_FOLDER,
    DEFAULT_STEAM_FOLDER,
)
from defaults import (
    ACTUAL_TPLUS_LOCATION,
    TPLUS_BIN_LOCATION,
    TPLUS_COMPATIBILITY_TOOL_DIR,
)
from file_system import FileSystem
from handlers.base_handler import BaseHandler

INSTALL_COMMAND = "install"

LAUNCHER_SCRIPT_TEMPLATE = """#!/bin/bash
cd "{tplus_location}"
uv run main.py "$@"
"""


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
        install_parser = subparser.add_parser(  # pyright: ignore[reportAny]
            INSTALL_COMMAND, help="Install as Steam compatibility tool"
        )
        install_parser.add_argument(  # pyright: ignore[reportAny]
            "--dry", action="store_true", help="Run in DRY mode (no filesystem changes)"
        )

    @override
    def handle(
        self,
        args: object,
        logger: logging.Logger,
    ) -> None:
        """
        Installs Tinker-Plus as a Steam compatibility tool.

        Regenerates the `tinker-plus.sh` launcher script so it points at wherever
        this checkout actually lives, symlinks it into the configured bin location,
        recreates the compatibility tool directory under Steam's actual
        `compatibilitytools.d` folder, and copies/symlinks the manifest and
        launcher files into it so Steam can discover and launch it.
        """
        dry_run = getattr(args, "dry", False)
        tinker_plus_sh_path = os.path.join(ACTUAL_TPLUS_LOCATION, "tinker-plus.sh")
        resources_dir = os.path.join(ACTUAL_TPLUS_LOCATION, "resources")
        compat_tools_dir = Path(
            DEFAULT_STEAM_COMPATIBILITY_TOOLS_FOLDER.format(DEFAULT_STEAM_FOLDER)
        )
        compat_path = compat_tools_dir / TPLUS_COMPATIBILITY_TOOL_DIR

        launcher_script = LAUNCHER_SCRIPT_TEMPLATE.format(
            tplus_location=ACTUAL_TPLUS_LOCATION
        )
        if dry_run:
            logger.info(
                "Dry run: would (re)generate launcher script at '%s' for this checkout",
                tinker_plus_sh_path,
            )
        else:
            # Generated fresh on every install so it always points at wherever this
            # checkout actually lives, instead of shipping a static script with a
            # path baked in at commit time.
            logger.info(
                "Generating launcher script at '%s'", tinker_plus_sh_path
            )
            with open(tinker_plus_sh_path, "w", encoding="utf-8") as f:
                _ = f.write(launcher_script)
            os.chmod(
                tinker_plus_sh_path,
                os.stat(tinker_plus_sh_path).st_mode | stat.S_IEXEC,
            )

        if dry_run:
            logger.info(
                "Dry run: would create symbolic link for Tinker-Plus (tplus) in '%s'",
                TPLUS_BIN_LOCATION,
            )
        else:
            logger.info(
                "Creating symbolic link for Tinker-Plus (tplus) in '%s'",
                TPLUS_BIN_LOCATION,
            )
            FileSystem.create_symbolic_link(
                tinker_plus_sh_path, TPLUS_BIN_LOCATION, logger
            )

        # Check if the compatibility tool directory exists, and remove it if it does.
        if compat_path.exists() and compat_path.is_dir():
            if dry_run:
                logger.info(
                    "Dry run: would remove existing compatibility tool directory at '%s'",
                    compat_path,
                )
            else:
                logger.info(
                    "Removing existing compatibility tool directory at '%s'",
                    compat_path,
                )
                shutil.rmtree(compat_path)

        if dry_run:
            logger.info(
                "Dry run: would install as Steam compatibility tool at '%s'", compat_path
            )
            return

        logger.info(
            "Installing as Steam compatibility tool at '%s'",
            compat_path,
        )
        compat_path.mkdir(parents=True, exist_ok=True)
        files_to_copy = {
            "toolmanifest.vdf": os.path.join(resources_dir, "toolmanifest.vdf"),
            "compatibilitytool.vdf": os.path.join(resources_dir, "compatibilitytool.vdf"),
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
