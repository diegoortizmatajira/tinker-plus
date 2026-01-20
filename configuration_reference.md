# Configuration values reference


| Property | Type | Default value | Description |
| -------- | ---- | ------------- | ----------- |
|BACKUP_ARCHIVE_COMMAND|str|7za a -y -m0=lzma2 -mx=9 -mmt8 "{archive}" "{source}"|The command used to create a backup archive of the game files.Use {archive} for the archive path and {source} for the source path.|
|BACKUP_ARCHIVE_NAME_TEMPLATE|str|{game_name} ({steam_game_id}).7z|Template for naming the backup archive files.Use {game_name} for the game name and {steam_game_id} for the Steam game ID.|
|BACKUP_LOCATION|str|None|The location where game files are backed up|
|BACKUP_RESTORE_COMMAND|str|7za x -y -o"{destination}" "{archive}"|The command used to restore game files from the backup archive.Use {archive} for the archive path and {destination} for the destination path.|
|BACKUP_RESTORE_IF_NOT_INSTALLED|bool|False|If enabled, the system will attempt to restore game files from the backup location if they are not found in the expected installation path when launching the game.|
|CONTEXT_COMMAND_AFTER_EXIT|str|None|Command that will be executed after exiting the game.|
|CONTEXT_COMMAND_BEFORE_STARTUP|str|None|Command that will be executed before starting the game.|
|GAMEMODERUN_ENABLED|bool|False|Enables GameModeRun when set to 'True'.|
|GAMESCOPE_ARGS|str|None|Additional arguments to pass to Gamescope.|
|GAMESCOPE_ENABLED|bool|False|Enables Gamescope when set to 'True'.|
|GAME_CUSTOM_ARGS|str|None|Allows specifying additional arguments for the game executable.|
|GAME_CUSTOM_CWD|str|None|Allows specifying a custom working directory for the game executable.|
|GAME_CUSTOM_EXE|str|None|Allows specifying the main game executable to run.|
|GAME_RUN_FORKS_ONLY|bool|False|If set to 'True', only the forked commands will be executed, skipping the main game command.|
|GENERAL_LOG_INDIVIDUAL_EXE|bool|False|If set to True, logs each individual executable that is run in is own file.|
|GUI_AUTORUN_TIMEOUT|int|3|Time in seconds before the GUI automatically starts the last launched game. Set to 0 to disable.|
|GUI_CLOSE_AFTER_RUNNING_GAME|bool|True|If true, closes the GUI after launching a game|
|GUI_SHOW_UI|bool|True|If true, shows the GUI on startup|
|LINK_PUBLIC_USER_FOLDER|str|None|If provided links the public user folder to the given location|
|LINK_SHOULD_BACKUP_FOLDERS|bool|True|If true, backups the user folders before linking them|
|LINK_STEAM_USER_FOLDER|str|None|If provided links the steam user folder to the given location|
|MANGOHUD_CONFIG|str|None|Configuration string for MangoHUD.|
|MANGOHUD_ENABLED|bool|False|Enables MangoHUD when set to 'True'.|
|PREFIX_CUSTOM_PATH|str|None|Allows selection of a specific prefix.|
|PROTON_DISABLE_NVAPI|bool|None|Disable Proton support for Nvidia's NVAPI GPU and DLSS (in Proton 9 or later)|
|PROTON_DLSS_INDICATOR|bool|None|Enables an on-screen indicator when DLSS is active in Proton games.|
|PROTON_DXVK_D3D8|bool|None|Enable DXVK's D3D8 support|
|PROTON_ENABLE_HDR|bool|None|Enable HDR support in Proton|
|PROTON_ENABLE_NVAPI|bool|None|Enables Proton support for Nvidia's NVAPI GPU and DLSS (in Proton 8 or earlier)|
|PROTON_ENABLE_WAYLAND|bool|None|Enable Wayland support in Proton|
|PROTON_FORCE_LARGE_ADDRESS_AWARE|bool|None|Force Wine to enable the LARGE_ADDRESS_AWARE flag|
|PROTON_FSR4_INDICATOR|bool|None|Enables an on-screen indicator when FSR 4 is active in Proton games.|
|PROTON_HIDE_NVIDIA_GPU|bool|None|Proton hide Nvidia GPU|
|PROTON_LOG|bool|None|Enables proton logging when set to 'True'.|
|PROTON_NO_D3D10|bool|None|Disable d3d10.dll and dxgi.dll, for D3D10 games which can fall back to and run better with D3D9|
|PROTON_NO_D3D11|bool|None|Disable d3d11.dll, for D3D11 games which can fall back to and run better with D3D9|
|PROTON_NO_ESYNC|bool|None|Do not use eventfd-based in-process synchronization primitives|
|PROTON_NO_FSYNC|bool|None|Do not use futex-based in-process synchronization primitives|
|PROTON_PREFER_SDL|bool|None|Expose SDL video driver along with Hidraw (Can fix input issues in some games)|
|PROTON_USE_WINED3D|bool|None|Use OpenGL-based WineD3D instead of Vulkan-based DXVK for D3D11, D3D10 and D3D9|
|PROTON_USE_WOW64|bool|None|Enable Proton WoW64 (32-bit Wine prefix) support|
|PROTON_VERSION|str|None|Defines which proton version to use.|
|SDL_VIDEODRIVER|str|None|Simple DirectMedia Layer (SDL) video driver to use.|
|STEAM_DEFAULT_REAPER_COMMAND|str|ubuntu12_32/reaper|Specifies the default command to use for Steam Reaper if none is set.|
|STEAM_DEFAULT_SNIPER_COMMAND|str|steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun|Specifies the default command to use for Steam Sniper if none is set.|
|STEAM_DEFAULT_WRAPPER_COMMAND|str|ubuntu12_32/steam-launch-wrapper|Specifies the default command to use for the Steam wrapper if none is set.|
|STEAM_USE_REAPER|bool|True|Enables the use of Reaper for Steam games when set to 'True'.|
|STEAM_USE_SNIPER|bool|True|Enables the use of Sniper for Steam games when set to 'True'.|
|STEAM_USE_WRAPPER|bool|False|Enables the use of Steam wrapper for Steam games when set to 'True'.|
|TRAINER_ARGS|str|None|Allows providing custom args to the trainer program.|
|TRAINER_ENABLED|bool|True|Enables custom trainer launching.|
|TRAINER_EXE|str|None|Allows selection of a specific trainer excecutable program.|
|UMU_RUN_BINARY|str|umu-run|Specifies the file path to the Umu Launcher executable.|
|UMU_RUN_ENABLED|bool|False|Enables the Umu runner for supported applications when set to 'True'.|
|UMU_RUN_USE_STEAM_PREFIX|bool|True|If enabled, Umu will utilize the Steam prefix for launching games.|
|WEMOD_ENABLED|bool|False|Enables WeMod integration for trainer launching.|
|WEMOD_EXE|str|None|Specifies the path to the WeMod executable.|
|WEMOD_GAMEID|str|None|Specifies the WeMod game ID for the target game.|
|WEMOD_OPEN_WITHOUT_GAMEID|bool|False|Specifies whether to open WeMod without a specific game ID.|
|WEMOD_WINETRICKS_REQUIREMENTS|list|['dotnet48', 'dotnetdesktop6']|Specifies the Winetricks requirements for WeMod integration.|
|WINETRICKS|list|[]|Specifies a list of winetricks packages to install (comma separated).|
|WINETRICKS_RUN|bool|True|Specifies if winetricks should be run (true/false).|
|WINE_DLLOVERRIDES|str|None|Specifies custom DLL overrides for Wine. The value should be a semicolon-separated list of DLL names and their override settings (e.g., 'dll1,native;dll2,builtin').|
|WINE_FULLSCREEN_FSR|bool|None|Enables Fullscreen FSR (FidelityFX Super Resolution) mode in Wine|
|WINE_FULLSCREEN_FSR_CUSTOM_MODE|str|None|Sets a custom Fullscreen FSR mode for Wine when 'custom' is selected in the Fullscreen FSR Mode setting. The value should be a resolution scale factor (e.g., '1.5' for 150% scaling).|
|WINE_FULLSCREEN_FSR_MODE|str|None|Sets the Fullscreen FSR mode for Wine.|
|WINE_WINDOWS_VERSION|str|None|Specifies the Windows version that Wine should emulate. Common values include 'win7', 'win10', etc.|
