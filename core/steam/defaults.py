"""Default paths for Steam and related tools."""

import os


DEFAULT_STEAM_FOLDER = os.path.expandvars("$HOME/.local/share/Steam")
DEFAULT_STEAM_COMMON_FOLDER = "{}/steamapps/common"
DEFAULT_STEAM_COMPATIBILITY_TOOLS_FOLDER = "{}/compatibilitytools.d"
DEFAULT_STEAM_WRAPPER = "{}/ubuntu12_32/steam-launch-wrapper"
DEFAULT_STEAM_REAPER = "{}/ubuntu12_32/reaper"
DEFAULT_STEAM_SNIPER = "{}/steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun"
DEFAULT_STEAM_APP_CACHE_FOLDER = "{}/appcache/librarycache/{}"
STEAM_MANIFESTS_TEMPLATE = "{}/steamapps/appmanifest_{}.acf"
