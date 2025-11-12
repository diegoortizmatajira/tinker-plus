import unittest

from core import RuntimeConfiguration
from core.runtime_provider import parse_command


class TestParseCommand(unittest.TestCase):
    def test_parse_command_basic(self):
        command = [
            "/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-launch-wrapper",
            "/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/reaper",
            "SteamLaunch",
            "AppId=367520",
            "/home/diegoortizmatajira/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point",
            "--verb=waitforexitandrun",
            "--",
            "/home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d/GE-Proton10-25/proton",
            "waitforexitandrun",
            "/home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow",
            "Knight/hollow_knight.exe",
        ]
        # [
        #     "/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-launch-wrapper",
        #     "/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/reaper",
        #     "SteamLaunch AppId=367520",
        #     "--",
        #     "/home/diegoortizmatajira/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper"
        #     + "/_v2-entry-point",
        #     "--verb=waitforexitandrun",
        #     "--",
        #     "/home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d/GE-Proton10-25"
        #     + "/proton waitforexitandrun",
        #     "/home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow",
        #     "Knight/hollow_knight.exe",
        # ]
        runtime_configuration = RuntimeConfiguration(command)
        parse_command(runtime_configuration)
        self.assertEqual(
            "/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/steam-launch-wrapper",
            runtime_configuration.steam_wrapper,
        )
        self.assertEqual(
            "/home/diegoortizmatajira/.local/share/Steam/ubuntu12_32/reaper",
            runtime_configuration.steam_reaper,
        )
        self.assertEqual(
            "/home/diegoortizmatajira/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper"
            + "/_v2-entry-point --verb=waitforexitandrun",
            runtime_configuration.steam_sniper,
        )
        self.assertEqual(
            "/home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d/GE-Proton10-25/proton waitforexitandrun",
            runtime_configuration.steam_compatibility_command,
        )
        self.assertEqual(
            "/home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d",
            runtime_configuration.steam_compatibility_tools_path,
        )
        self.assertEqual(
            "GE-Proton10-25",
            runtime_configuration.steam_compatibility_tool,
        )
        self.assertEqual(
            "/home/diegoortizmatajira/.local/share/Steam/steamapps/common/Hollow Knight"
            + "/hollow_knight.exe",
            runtime_configuration.steam_game_exe,
        )
