# Configuration values reference


| Property | Type | Default value | Description |
| -------- | ---- | ------------- | ----------- |
|GAMEMODERUN_ENABLED|bool|False|Enables GameModeRun when set to 'True'.|
|GAMESCOPE_ARGS|str|None|Additional arguments to pass to Gamescope.|
|GAMESCOPE_ENABLED|bool|False|Enables Gamescope when set to 'True'.|
|GAME_CUSTOM_ARGS|str|None|Allows specifying additional arguments for the game executable.|
|GAME_CUSTOM_EXE|str|None|Allows specifying the main game executable to run.|
|GAME_RUN_FORKS_ONLY|bool|False|If set to 'True', only the forked commands will be executed, skipping the main game command.|
|GENERAL_LOG_INDIVIDUAL_EXE|bool|False|If set to True, logs each individual executable that is run in is own file.|
|LINK_PUBLIC_USER_FOLDER|str|None|If provided links the public user folder to the given location|
|LINK_SHOULD_BACKUP_FOLDERS|bool|True|If true, backups the user folders before linking them|
|LINK_STEAM_USER_FOLDER|str|None|If provided links the steam user folder to the given location|
|PREFIX_CUSTOM_PATH|str|None|Allows selection of a specific prefix.|
|PROTON_DISABLE_NVAPI|bool|None|Disable Proton support for Nvidia's NVAPI GPU and DLSS|
|PROTON_DXVK_D3D8|bool|None|Enable DXVK's D3D8 support|
|PROTON_FORCE_LARGE_ADDRESS_AWARE|bool|None|Force Wine to enable the LARGE_ADDRESS_AWARE flag|
|PROTON_HIDE_NVIDIA_GPU|bool|None|Proton hide Nvidia GPU|
|PROTON_LOG|bool|None|Enables proton logging when set to 'True'.|
|PROTON_NO_D3D10|bool|None|Disable d3d10.dll and dxgi.dll, for D3D10 games which can fall back to and run better with D3D9|
|PROTON_NO_D3D11|bool|None|Disable d3d11.dll, for D3D11 games which can fall back to and run better with D3D9|
|PROTON_NO_ESYNC|bool|None|Do not use eventfd-based in-process synchronization primitives|
|PROTON_NO_FSYNC|bool|None|Do not use futex-based in-process synchronization primitives|
|PROTON_USE_WINED3D|bool|None|Use OpenGL-based WineD3D instead of Vulkan-based DXVK for D3D11, D3D10 and D3D9|
|PROTON_VERSION|str|None|Defines which proton version to use.|
|SDL_VIDEODRIVER|str|None|Simple DirectMedia Layer (SDL) video driver to use.|
|STEAM_LAST_REAPER_COMMAND|str|None|Stores the last Reaper command used for Steam games.|
|STEAM_LAST_SNIPER_COMMAND|str|None|Stores the last Sniper command used for Steam games.|
|STEAM_LAST_WRAPPER_COMMAND|str|None|Stores the last wrapper command used for Steam games.|
|STEAM_USE_REAPER|bool|True|Enables the use of Reaper for Steam games when set to 'True'.|
|STEAM_USE_SNIPER|bool|True|Enables the use of Sniper for Steam games when set to 'True'.|
|STEAM_USE_WRAPPER|bool|False|Enables the use of Steam wrapper for Steam games when set to 'True'.|
|TRAINER_ARGS|str|None|Allows providing custom args to the trainer program.|
|TRAINER_ENABLED|bool|True|Enables custom trainer launching.|
|TRAINER_EXE|str|None|Allows selection of a specific trainer excecutable program.|
|WEMOD_ENABLED|bool|False|Enables WeMod integration for trainer launching.|
|WEMOD_EXE|str|None|Specifies the path to the WeMod executable.|
|WEMOD_GAMEID|str|None|Specifies the WeMod game ID for the target game.|
|WEMOD_WINETRICKS_REQUIREMENTS|list|['dotnet48']|Specifies the Winetricks requirements for WeMod integration.|
|WINETRICKS|list|[]|Specifies a list of winetricks packages to install (comma separated).|
|WINETRICKS_RUN|bool|True|Specifies if winetricks should be run (true/false).|
|WINE_DLLOVERRIDES|str|None|Specifies custom DLL overrides for Wine. The value should be a semicolon-separated list of DLL names and their override settings (e.g., 'dll1,native;dll2,builtin').|
