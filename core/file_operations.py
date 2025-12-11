"""Module for file operations such as creating symbolic links."""

import logging
import json
import os
import shutil
from os.path import islink
from pathlib import Path
from typing import Any

from core.defaults import (
    GAME_CONFIG_FILE_TEMPLATE,
    GAME_LOGS_DIR_TEMPLATE,
    GAME_SCRIPT_TEMPLATE,
    HUMAN_READABLE_LINKS_DIR_TEMPLATE,
    LOG_DRY_RUN,
    LOG_EXECUTING,
)
from core.game_info import GameInfo


def delete_folder_tree(folder_path: str, logger: logging.Logger, *, dry_run: bool):
    """
    Deletes a folder and all its contents.

    Args:
        folder_path (str): The path of the folder to delete.
        logger (logging.Logger): The logger instance for logging progress and errors.
        dry_run (bool): If True, only logs the deletion without performing it.
    """
    try:
        location = Path(folder_path)

        if location.exists() and location.is_dir():
            if dry_run:
                logger.info(
                    LOG_DRY_RUN.format("Dry run: would delete folder tree at %s"),
                    folder_path,
                )
            else:
                shutil.rmtree(location)
                logger.info("Deleted folder tree at %s", folder_path)
        else:
            logger.info("Folder does not exist, skipping deletion: %s", folder_path)
    except Exception as e:
        logger.error("Error deleting folder tree at %s: %s", folder_path, e)
        raise RuntimeError(f"Error deleting folder tree at {folder_path}") from e


def create_symbolic_link(
    target: str, link_name: str, logger: logging.Logger, *, should_backup: bool = True
):
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
                if should_backup:
                    backup_location = location.parent / (location.name + "_backup")
                    os.rename(location, backup_location)
                    logger.info(
                        "Backed up existing %s folder to '%s'",
                        location.name,
                        backup_location,
                    )
                else:
                    shutil.rmtree(location)
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
                if should_backup:
                    backup_location = location.parent / (location.name + ".backup")
                    os.rename(location, backup_location)
                    logger.info(
                        "Backed up existing %s file to '%s'",
                        location.name,
                        backup_location,
                    )
                else:
                    location.unlink()
        target_path = Path(target)
        os.symlink(target_path, location)
        logger.info(
            LOG_EXECUTING.format("Created symbolic link %s -> %s"),
            location,
            target_path,
        )
    except Exception as e:
        logger.error("Error creating symbolic link %s -> %s: %s", link_name, target, e)
        raise RuntimeError(
            f"Error creating symbolic link {link_name} -> {target}"
        ) from e


def remove_tplus_game_files(game_id: str, logger: logging.Logger):
    """
    Removes specific TPlus files associated with a game.

    Args:
        game_id (str): The identifier for the game.
        logger (logging.Logger): The logger instance for logging progress and errors.
    """
    delete_queue = [
        GAME_CONFIG_FILE_TEMPLATE.format(game_id),
        GAME_LOGS_DIR_TEMPLATE.format(game_id),
        GAME_SCRIPT_TEMPLATE.format(game_id),
    ]
    game_info = GameInfo.from_cache(game_id, logger)
    if game_info:
        delete_queue.append(HUMAN_READABLE_LINKS_DIR_TEMPLATE.format(game_info.name))

    for item_path in delete_queue:
        try:
            path = Path(item_path)
            if not path.exists():
                logger.info("Item does not exist, skipping: %s", item_path)
                continue
            if path.is_file():
                path.unlink()
                logger.info("Removed file: %s", item_path)
            elif path.is_dir():
                shutil.rmtree(path)
                logger.info("Removed directory: %s", item_path)
        except Exception as e:
            logger.error("Error removing TPlus file %s: %s", item_path, e)
            raise RuntimeError(f"Error removing TPlus file {item_path}") from e


def dump_as_json(
    data: dict[str, Any], file_path: str, dry_run: bool, logger: logging.Logger
):
    """
    Dumps a dictionary as a JSON file.

    Args:
        data (dict): The data to be dumped as JSON.
        file_path (str): The path of the file where the JSON data will be saved.
        logger (logging.Logger): The logger instance for logging progress and errors.
    """
    if dry_run:
        logger.info(
            LOG_DRY_RUN.format("Dry run: would dump data to JSON file at %s"),
            file_path,
        )
        return
    try:
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, sort_keys=True)
        logger.debug("Data persisted to a JSON file at %s", file_path)
    except Exception as e:
        logger.error("Error dumping data to JSON file at %s: %s", file_path, e)
        raise RuntimeError(f"Error dumping data to JSON file at {file_path}") from e
