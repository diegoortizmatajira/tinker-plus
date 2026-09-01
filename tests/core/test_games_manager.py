import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.config_storage import ConfigStorage
from core.games_manager import GamesManager
from model import GameInfo


class TestGamesManager(unittest.TestCase):
    def _make_storage(self, filenames: list[str]) -> ConfigStorage:
        storage = MagicMock(spec=ConfigStorage)
        storage.get_game_configuration_files.return_value = [
            Path(f"/config/game_configs/{name}.json") for name in filenames
        ]
        return storage

    @patch("core.games_manager.GameInfoRepository.from_cache")
    def test_get_games_sorted_case_insensitively(self, mock_from_cache: MagicMock):
        storage = self._make_storage(["1", "2", "3"])
        mock_from_cache.side_effect = [
            GameInfo("1", "zelda"),
            GameInfo("2", "Age of Empires"),
            GameInfo("3", "hollow knight"),
        ]
        manager = GamesManager(storage)
        self.assertEqual(
            [g.name for g in manager.get_games()],
            ["Age of Empires", "hollow knight", "zelda"],
        )

    @patch("core.games_manager.GameInfoRepository.from_cache")
    def test_get_games_filters_out_missing_cache_entries(self, mock_from_cache: MagicMock):
        storage = self._make_storage(["1", "2"])
        mock_from_cache.side_effect = [GameInfo("1", "Known Game"), None]
        manager = GamesManager(storage)
        self.assertEqual([g.name for g in manager.get_games()], ["Known Game"])

    @patch("core.games_manager.GameInfoRepository.from_cache")
    def test_get_games_empty_when_no_configuration_files(self, mock_from_cache: MagicMock):
        storage = self._make_storage([])
        manager = GamesManager(storage)
        self.assertEqual(manager.get_games(), [])
        mock_from_cache.assert_not_called()

    @patch("core.games_manager.GameInfoRepository.from_cache")
    def test_constructor_loads_games_immediately(self, mock_from_cache: MagicMock):
        storage = self._make_storage(["1"])
        mock_from_cache.return_value = GameInfo("1", "Loaded On Init")
        manager = GamesManager(storage)
        # No need to call get_configured_games() again - it already ran in __init__.
        self.assertEqual(manager.get_games()[0].name, "Loaded On Init")


if __name__ == "__main__":
    _ = unittest.main()
