LOAD_ENV = set -a; . ./.env; set +a;

test:
	$(LOAD_ENV) tplus --debug run --dry gamemoderun /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-launch-wrapper /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/reaper SteamLaunch AppId=367520 -- /home/diegoortizmatajira/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun -- /home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d/GE-Proton10-25/proton waitforexitandrun /home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight/hollow_knight.exe
test_nogui:
	$(LOAD_ENV) tplus --debug run --nogui --dry gamemoderun /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-launch-wrapper /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/reaper SteamLaunch AppId=367520 -- /home/diegoortizmatajira/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun -- /home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d/GE-Proton10-25/proton waitforexitandrun /home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight/hollow_knight.exe
test_gui:
	$(LOAD_ENV) tplus --debug run --gui --dry gamemoderun /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-launch-wrapper /home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/reaper SteamLaunch AppId=367520 -- /home/diegoortizmatajira/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun -- /home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d/GE-Proton10-25/proton waitforexitandrun /home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight/hollow_knight.exe
test_compat_tool:
	$(LOAD_ENV) tplus --debug run --dry /home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight/hollow_knight.exe
test_action:
	$(LOAD_ENV) tplus --debug execute prepare-wemod
generate_documentation:
	$(LOAD_ENV) tplus generate_documentation
