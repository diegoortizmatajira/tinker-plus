"""
Module for handling Steam environment data parsing and storage.
"""

from dataclasses import dataclass


@dataclass
class SteamEnvironmentData:
    """
    Data class to hold Steam environment data and parse relevant information
    """

    steam_app_id: str | None = None
    steam_game_id: str | None = None
    steam_compat_client_install_path: str | None = None
    steam_compat_install_path: str | None = None
    steam_fossilize_dump_path: str | None = None
    steam_runtime: str | None = None
    steam_client_config_file: str | None = None
    steam_compat_shader_path: str | None = None
    ld_preload: str | None = None
    steamscript_version: str | None = None
    steam_compat_media_path: str | None = None
    steam_compat_app_id: str | None = None
    steam_compat_data_path: str | None = None
    steam_compat_transcoded_media_path: str | None = None
    steam_base_folder: str | None = None
    cmd_steam_wrapper: str | None = None
    cmd_steam_reaper: str | None = None
    cmd_steam_sniper: str | None = None
    cmd_steam_compatibility_command: str | None = None
    cmd_steam_compatibility_tool: str | None = None
    cmd_steam_compatibility_tools_path: str | None = None
    cmd_steam_game_exe: str | None = None
    cmd_steam_game_args: str | None = None

    @staticmethod
    def empty() -> "SteamEnvironmentData":
        """
        Creates and returns an instance of SteamEnvironmentData with all fields set to None.

        Returns:
            SteamEnvironmentData: An instance with all attributes initialized to None.
        """
        return SteamEnvironmentData()
