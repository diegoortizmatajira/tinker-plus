import unittest

from model import SteamEnvironmentData


PART_WRAPPER = "wrapper"
PART_REAPER = "reaper"
PART_SNIPER = "sniper"
PART_COMPATIBILITY_COMMAND = "compatibility_command"
PART_GAME_EXE = "game_exe"
PART_GAME_ARGS = "game_args"

EXAMPLE_COMMAND = {
    PART_WRAPPER: "/home/steamuser/.local/share/Steam/ubuntu12_32/steam-launch-wrapper",
    PART_REAPER: "/home/steamuser/.local/share/Steam/ubuntu12_32/reaper",
    PART_SNIPER: "/home/steamuser/.local/share/Steam/steamapps/common"
    + "/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun",
    PART_COMPATIBILITY_COMMAND: "/home/steamuser/.local/share/Steam"
    + "/compatibilitytools.d/GE-Proton10-25/proton waitforexitandrun",
    PART_GAME_EXE: "/home/steamuser/.local/share/Steam/steamapps"
    + "/common/Hollow Knight/hollow_knight.exe",
    PART_GAME_ARGS: "-arg1",
}


class TestParseCommand(unittest.TestCase):
    def build_command(self, parts: dict[str, str]) -> list[str]:
        order = [
            PART_WRAPPER,
            PART_REAPER,
            PART_SNIPER,
            PART_COMPATIBILITY_COMMAND,
            PART_GAME_EXE,
            PART_GAME_ARGS,
        ]
        return " ".join([parts[part] for part in order if part in parts]).split(" ")

    def parse_command_basic(self, command_dict: dict[str, str]):
        command_dict = EXAMPLE_COMMAND
        command = self.build_command(command_dict)
        env_data = SteamEnvironmentData()
        env_data.parse_steam_command(" ".join(command))
        self.assertEqual(
            command_dict.get(PART_WRAPPER),
            env_data.cmd_steam_wrapper,
        )
        self.assertEqual(
            command_dict.get(PART_REAPER),
            env_data.cmd_steam_reaper,
        )
        self.assertEqual(
            command_dict.get(PART_SNIPER),
            env_data.cmd_steam_sniper,
        )
        self.assertEqual(
            command_dict.get(PART_COMPATIBILITY_COMMAND),
            env_data.cmd_steam_compatibility_command,
        )
        self.assertEqual(
            command_dict.get(PART_GAME_EXE),
            env_data.cmd_steam_game_exe,
        )

    def test_parse_command_full(self):
        self.parse_command_basic(EXAMPLE_COMMAND)

    def test_parse_command_without_parts(self):
        parts = [
            PART_WRAPPER,
            PART_REAPER,
            PART_SNIPER,
            PART_COMPATIBILITY_COMMAND,
            PART_GAME_EXE,
            PART_GAME_ARGS,
        ]
        for part in parts:
            with self.subTest(part=part):
                test_command = EXAMPLE_COMMAND.copy()
                del test_command[part]
                self.assertNotIn(part, test_command)
                self.parse_command_basic(test_command)

    def test_parse_executables(self):
        # pylint: disable=line-too-long
        test_executables = [
            "/home/steamuser/.local/share/Steam/steamapps/common/Assassin's Creed IV Black Flag/AC4BFSP.exe",
            "/home/steamuser/.local/share/Steam/steamapps/common/A Plague Tale Requiem/APlagueTaleRequiem_x64.exe",
            "/home/steamuser/.local/share/Steam/steamapps/common/Baldurs Gate 3/Launcher.exe",
            "/home/steamuser/.local/share/Steam/steamapps/common/Marvel's Spider-Man 2/Spider-Man2.exe",
            "/home/steamuser/.local/share/Steam/steamapps/common/Boltgun/Warhammer 40,000 Boltgun.exe",
        ]
        for executable in test_executables:
            with self.subTest(executable=executable):
                command_dict = EXAMPLE_COMMAND.copy()
                command_dict[PART_GAME_EXE] = executable
                command = self.build_command(command_dict)
                env_data = SteamEnvironmentData()
                env_data.parse_steam_command(" ".join(command))
                self.assertEqual(
                    executable,
                    env_data.cmd_steam_game_exe,
                )

    def test_parse_invalid_executables(self):
        test_executables = [
            "/home/steamuser/.local/share/Steam/steamapps/common/Invalid/Invalid#1.exe",
            "/home/steamuser/.local/share/Steam/steamapps/common/Invalid/Invalid$1.exe",
            "/home/steamuser/.local/share/Steam/steamapps/common/Invalid/Invalid=1.exe",
        ]
        for executable in test_executables:
            with self.subTest(executable=executable):
                command_dict = EXAMPLE_COMMAND.copy()
                command_dict[PART_GAME_EXE] = executable
                command = self.build_command(command_dict)
                env_data = SteamEnvironmentData()
                with self.assertRaises(RuntimeError):
                    env_data.parse_steam_command(" ".join(command))

    def test_parse_compatibility_tools(self):
        # pylint: disable=line-too-long
        test_compat_tools = [
            "/home/diegoortizmatajira/.local/share/Steam/steamapps/common/Proton 8.0/proton waitforexitandrun",
            "/home/diegoortizmatajira/.local/share/Steam/compatibilitytools.d/GE-Proton-10-25/proton waitforexitandrun",
        ]
        for compat_tool in test_compat_tools:
            with self.subTest(executable=compat_tool):
                command_dict = EXAMPLE_COMMAND.copy()
                command_dict[PART_COMPATIBILITY_COMMAND] = compat_tool
                command = self.build_command(command_dict)
                env_data = SteamEnvironmentData()
                env_data.parse_steam_command(" ".join(command))
                self.assertEqual(
                    compat_tool,
                    env_data.cmd_steam_compatibility_command,
                )
