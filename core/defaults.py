"""
Default configuration values for Tinker Plus application.
"""

import os

CONFIG_LOCATION = os.path.expandvars("$HOME/.config/tinker-plus")
GLOBAL_CONFIG_FILE = f"{CONFIG_LOCATION}/global_config.json"
GAME_CONFIG_DIR = f"{CONFIG_LOCATION}/game_configs"
GAME_CONFIG_FILE_TEMPLATE = f"{GAME_CONFIG_DIR}/{{}}.json"
LOGS_DIR = f"{CONFIG_LOCATION}/logs"
PROTON_LOGS_DIR = f"{LOGS_DIR}/proton"
APP_LOGS_DIR = f"{LOGS_DIR}/app"
APP_LOG_FILE = f"{APP_LOGS_DIR}/tinker-plus.log"
