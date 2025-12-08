"""
Default configuration values for Tinker Plus application.
"""

import os
from datetime import datetime


def timestamped_log(folder: str, base: str) -> str:
    """Generate a log file name with a timestamp."""
    return f"{folder}/{base}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"


ACTUAL_TPLUS_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_STEAM_FOLDER = os.path.expandvars("$HOME/.local/share/Steam")
DEFAULT_STEAM_COMMON_FOLDER = "{}/steamapps/common"
DEFAULT_STEAM_COMPATIBILITY_TOOLS_FOLDER = "{}/compatibilitytools.d"
DEFAULT_STEAM_WRAPPER = "{}/ubuntu12_32/steam-launch-wrapper"
DEFAULT_STEAM_REAPER = "{}/ubuntu12_32/reaper"
DEFAULT_STEAM_SNIPER = "{}/steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun"
DEFAULT_STEAM_APP_CACHE_FOLDER = "{}/appcache/librarycache/{}"

TPLUS_BIN_LOCATION = os.path.expandvars("$HOME/.local/bin/tplus")
TPLUS_COMPATIBILITY_TOOL_DIR = (
    f"{DEFAULT_STEAM_FOLDER}/compatibilitytools.d/Tinker-Plus"
)

CONFIG_LOCATION = os.path.expandvars("$HOME/.config/tinker-plus")
GLOBAL_CONFIG_FILE = f"{CONFIG_LOCATION}/global_config.json"
LAST_RUN_LOG_FILE = f"{CONFIG_LOCATION}/lastrun.log"
GLOBAL_GAME_INFO_CACHE_FILE = f"{CONFIG_LOCATION}/game_info_cache.json"
GLOBAL_COMPAT_TOOL_CACHE_FILE = f"{CONFIG_LOCATION}/compat_tool_cache.json"
GAME_CONFIG_DIR = f"{CONFIG_LOCATION}/game_configs"
GAME_CONFIG_FILE_TEMPLATE = f"{GAME_CONFIG_DIR}/{{}}.json"
LOGS_DIR = f"{CONFIG_LOCATION}/logs"
SCRIPTS_DIR = f"{CONFIG_LOCATION}/scripts"
GAME_LOGS_DIR_TEMPLATE = f"{LOGS_DIR}/{{}}"
GAME_SCRIPT_TEMPLATE = f"{SCRIPTS_DIR}/{{}}.sh"
HUMAN_READABLE_LINKS_DIR = f"{CONFIG_LOCATION}/games"
HUMAN_READABLE_LINKS_DIR_TEMPLATE = f"{HUMAN_READABLE_LINKS_DIR}/{{}}"

# Log files
APP_LAST_RUN_LOG_FILE = "lastrun.log"
PROTON_LOG_FILE = "proton.log"
# Common paths
USERS_DIR_NAME = "drive_c/users"
CWD_DIR_NAME = "drive_c/cwd"
STEAM_USER_FOLDER_NAME = f"{USERS_DIR_NAME}/steamuser"
PUBLIC_USER_FOLDER_NAME = f"{USERS_DIR_NAME}/Public"
STEAM_MANIFESTS_TEMPLATE = "{}/steamapps/appmanifest_{}.acf"

LOG_STAGE_STARTED = "🟢 STAGE STARTED: {}"
LOG_DRY_RUN = "ℹ️ DRY RUN: {}"
LOG_EXECUTING = "▶️ {}"
LOG_SEARCHING = "🔍 {}"
LOG_USER_ACTION = "👤 {}"
LOG_TIMER_ACTION = "⏱️ {}"

# Create directories if they do not exist
os.makedirs(GAME_CONFIG_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(HUMAN_READABLE_LINKS_DIR, exist_ok=True)
