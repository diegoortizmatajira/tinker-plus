"""
Default configuration values for Tinker Plus application.
"""

import os
from datetime import datetime


def timestamped_log(folder: str, base: str) -> str:
    """Generate a log file name with a timestamp."""
    return f"{folder}/{base}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"


CONFIG_LOCATION = os.path.expandvars("$HOME/.config/tinker-plus")
GLOBAL_CONFIG_FILE = f"{CONFIG_LOCATION}/global_config.json"
GAME_CONFIG_DIR = f"{CONFIG_LOCATION}/game_configs"
GAME_CONFIG_FILE_TEMPLATE = f"{GAME_CONFIG_DIR}/{{}}.json"
GAME_BAT_LAUNCHER_DIR = f"{CONFIG_LOCATION}/bat_launchers"
GAME_BAT_LAUNCHER_FILE_TEMPLATE = f"{GAME_BAT_LAUNCHER_DIR}/{{}}_launcher.bat"
LOGS_DIR = f"{CONFIG_LOCATION}/logs"
PROTON_LOG_DIR = f"{LOGS_DIR}/proton"
PROTON_LOG_FILE = timestamped_log(PROTON_LOG_DIR, "proton")
APP_LOGS_DIR = f"{LOGS_DIR}/app"
# Add dynamic date to the log file name
APP_LOG_FILE = timestamped_log(APP_LOGS_DIR, "tinker-plus")
GENERAL_TOOLS_LOG_DIR = f"{LOGS_DIR}/general"
GENERAL_TOOLS_LOG_FILE = timestamped_log(GENERAL_TOOLS_LOG_DIR, "tools")
WINETRICKS_LOG_FILE = timestamped_log(GENERAL_TOOLS_LOG_DIR, "winetricks")

# Create directories if they do not exist
os.makedirs(GAME_CONFIG_DIR, exist_ok=True)
os.makedirs(PROTON_LOG_DIR, exist_ok=True)
os.makedirs(APP_LOGS_DIR, exist_ok=True)
os.makedirs(GENERAL_TOOLS_LOG_DIR, exist_ok=True)
