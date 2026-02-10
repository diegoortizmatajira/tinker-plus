export
SteamAppId=367520
SteamGameId=367520
STEAM_BASE_FOLDER=/home/diegoortizmatajira/.local/share/Steam
STEAM_COMPAT_INSTALL_PATH="/home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight"
STEAM_COMPAT_DATA_PATH=/home/diegoortizmatajira/.local/share/Steam/steamapps/compatdata/367520
STEAM_COMPAT_CLIENT_INSTALL_PATH=/home/diegoortizmatajira/.local/share/Steam

STEAM_FOSSILIZE_DUMP_PATH=/home/diegoortizmatajira/.local/share/Steam/steamapps/shadercache/367520/fozpipelinesv6/steamapprun_pipeline_cache
STEAM_RUNTIME=/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime
STEAM_CLIENT_CONFIG_FILE=/home/diegoortizmatajira/.local/share/steam.cfg
STEAM_ZENITY=/usr/bin/zenity
STEAMSCRIPT_VERSION=1.0.0.85
STEAM_COMPAT_SHADER_PATH=/home/diegoortizmatajira/.local/share/Steam/steamapps/shadercache/367520
STEAM_COMPAT_MEDIA_PATH=/home/diegoortizmatajira/.local/share/Steam/steamapps/shadercache/367520/fozmediav1
STEAM_COMPAT_APP_ID=367520
STEAM_COMPAT_TRANSCODED_MEDIA_PATH=/home/diegoortizmatajira/.local/share/Steam/steamapps/shadercache/367520
STEAM_COMPAT_MOUNTS=
SteamVirtualGamepadInfo_Proton=/home/diegoortizmatajira/.local/share/Steam/config/virtualgamepadinfo.txt
STEAM_COMPAT_PROTON=1
STEAM_COMPAT_TOOL_PATHS=
STEAM_FOSSILIZE_DUMP_PATH_READ_ONLY=$bucketdir/steam_pipeline_cache.foz;$bucketdir/steamapp_pipeline_cache.foz
LD_LIBRARY_PATH=/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/pinned_libs_32:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/pinned_libs_64:/opt/intel/oneapi/compiler/latest/lib:/usr/lib32:/usr/lib/libfakeroot:/usr/lib:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/lib/i386-linux-gnu:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/usr/lib/i386-linux-gnu:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/lib/x86_64-linux-gnu:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/usr/lib/x86_64-linux-gnu:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/lib:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/usr/lib:/home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight
AMD_VK_PIPELINE_CACHE_FILENAME=steamapp_shader_cache
AMD_VK_PIPELINE_CACHE_PATH=/home/diegoortizmatajira/.local/share/Steam/steamapps/shadercache/367520/AMDv1
SteamClientLaunch=1
LD_PRELOAD=:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/gameoverlayrenderer.so:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_64/gameoverlayrenderer.so
MESA_GLSL_CACHE_MAX_SIZE=5G
FOSSILIZE_APPLICATION_INFO_FILTER_PATH=/home/diegoortizmatajira/.local/share/Steam/fossilize_engine_filters.json
ENABLE_VK_LAYER_VALVE_steam_fossilize_1=1
SDL_GAMECONTROLLER_ALLOW_STEAM_VIRTUAL_GAMEPAD=1
SRT_LAUNCHER_SERVICE_ALONGSIDE_STEAM=com.steampowered.PressureVessel.LaunchAlongsideSteam
DXVK_STATE_CACHE_PATH=/home/diegoortizmatajira/.local/share/Steam/steamapps/shadercache/367520/DXVK_state_cache
MESA_DISK_CACHE_READ_ONLY_FOZ_DBS=steam_cache,steam_precompiled
STEAMSCRIPT=/usr/lib/steam/steam
STEAM_COMPAT_FLAGS=search-cwd
SteamOverlayGameId=367520
__GL_SHADER_DISK_CACHE_APP_NAME=steamapp_shader_cache
SteamEnv=1
GIO_LAUNCHED_DESKTOP_FILE_PID=1970131
SDL_JOYSTICK_HIDAPI_STEAMXBOX=0
GIO_LAUNCHED_DESKTOP_FILE=/home/diegoortizmatajira/.local/share/applications/steam.desktop
STEAM_COMPAT_LIBRARY_PATHS=/home/diegoortizmatajira/.local/share/Steam/steamapps
SteamUser=diegoortizmatajira
OLDPWD=/home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight
STEAM_RUNTIME_LIBRARY_PATH=/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/pinned_libs_32:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/pinned_libs_64:/opt/intel/oneapi/compiler/latest/lib:/usr/lib32:/usr/lib/libfakeroot:/usr/lib:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/lib/i386-linux-gnu:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/usr/lib/i386-linux-gnu:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/lib/x86_64-linux-gnu:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/usr/lib/x86_64-linux-gnu:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/lib:/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-runtime/usr/lib
TEXTDOMAIN=steam

test:
	tplus --debug run --dry gamemoderun /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-launch-wrapper /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/reaper SteamLaunch AppId=367520 -- /home/diegoortizmatajira/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun -- /home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d/GE-Proton10-25/proton waitforexitandrun /home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight/hollow_knight.exe
test_nogui:
	tplus --debug run --nogui --dry gamemoderun /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-launch-wrapper /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/reaper SteamLaunch AppId=367520 -- /home/diegoortizmatajira/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun -- /home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d/GE-Proton10-25/proton waitforexitandrun /home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight/hollow_knight.exe
test_gui:
	tplus --debug run --gui --dry gamemoderun /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-launch-wrapper /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/reaper SteamLaunch AppId=367520 -- /home/diegoortizmatajira/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun -- /home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d/GE-Proton10-25/proton waitforexitandrun /home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight/hollow_knight.exe
test_compat_tool:
	tplus --debug run --dry /home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight/hollow_knight.exe
test_action:
	tplus --debug execute prepare-wemod
generate_documentation:
	tplus generate_documentation 
