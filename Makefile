export
SteamAppId=367520
SteamGameId=367520
STEAM_BASE_FOLDER=/home/diegoortizmatajira/.local/share/Steam
STEAM_COMPAT_INSTALL_PATH="/home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight"
STEAM_COMPAT_DATA_PATH=/home/diegoortizmatajira/.local/share/Steam/steamapps/compatdata/367520
STEAM_COMPAT_CLIENT_INSTALL_PATH=/home/diegoortizmatajira/.local/share/Steam

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
