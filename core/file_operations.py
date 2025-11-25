"""Module for file operations such as creating symbolic links."""

import logging
import os
from os.path import islink
from pathlib import Path


def create_symbolic_link(target: str, link_name: str, logger: logging.Logger):
    """
    Creates a symbolic link pointing to target named link_name.

    Args:
        target (str): The path the symbolic link points to.
        link_name (str): The path of the symbolic link to be created.
        logger (logging.Logger): The logger instance for logging progress and errors.
    """
    try:
        location = Path(link_name)

        if location.exists():
            if location.is_dir(follow_symlinks=False):
                backup_location = location.parent / (location.name + "_backup")
                os.rename(location, backup_location)
                logger.info(
                    "Backed up existing %s folder to '%s'",
                    location.name,
                    backup_location,
                )
            elif islink(location):
                # check if the existing link points to the correct target
                existing_target = os.readlink(location)
                if existing_target == target:
                    logger.info(
                        "Symbolic link %s already exists. Skipping creation.", link_name
                    )
                    return
                location.unlink()
            elif location.is_file(follow_symlinks=False):
                backup_location = location.parent / (location.name + ".backup")
                os.rename(location, backup_location)
                logger.info(
                    "Backed up existing %s file to '%s'", location.name, backup_location
                )
        target_path = Path(target)
        os.symlink(target_path, location, target_is_directory=target_path.is_dir())
        logger.info("Created symbolic link %s -> %s", location, target_path)
    except Exception as e:
        logger.error("Error creating symbolic link %s -> %s: %s", link_name, target, e)
        raise RuntimeError(
            f"Error creating symbolic link {link_name} -> {target}"
        ) from e
