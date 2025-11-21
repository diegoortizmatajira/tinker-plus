"""
Default configuration values for Tinker Plus application.
"""

import os
from datetime import datetime


def timestamped_log(folder: str, base: str) -> str:
    """Generate a log file name with a timestamp."""
    return f"{folder}/{base}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"


TPLUS_BIN_LOCATION = os.path.expandvars("$HOME/.local/bin/tplus")
CONFIG_LOCATION = os.path.expandvars("$HOME/.config/tinker-plus")
GLOBAL_CONFIG_FILE = f"{CONFIG_LOCATION}/global_config.json"
GAME_CONFIG_DIR = f"{CONFIG_LOCATION}/game_configs"
GAME_CONFIG_FILE_TEMPLATE = f"{GAME_CONFIG_DIR}/{{}}.json"
LOGS_DIR = f"{CONFIG_LOCATION}/logs"
GAME_LOGS_DIR_TEMPLATE = f"{LOGS_DIR}/{{}}"
# Log files
APP_LAST_RUN_LOG_FILE = "lastrun.log"
GENERAL_TOOLS_LOG_FILE = "tools.log"
WINETRICKS_LOG_FILE = "winetricks.log"
PROTON_LOG_FILE = "proton.log"
# Common paths
USERS_DIR_NAME = "drive_c/users"
STEAM_USER_FOLDER_NAME = f"{USERS_DIR_NAME}/steamuser"
PUBLIC_USER_FOLDER_NAME = f"{USERS_DIR_NAME}/Public"

# Create directories if they do not exist
os.makedirs(GAME_CONFIG_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
