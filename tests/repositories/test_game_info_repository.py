import json
import logging
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from model import GameInfo
from repositories.game_info_repository import GameInfoRepository

TEST_LOGGER = logging.getLogger("test")


class TestGameInfoRepository(unittest.TestCase):
    def setUp(self):
        GameInfoRepository._cache = None  # pyright: ignore[reportPrivateUsage]
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.tmp_dir, ignore_errors=True))
        self.cache_file = str(self.tmp_dir / "game_info_cache.json")
        self.patcher = patch(
            "repositories.game_info_repository.GLOBAL_GAME_INFO_CACHE_FILE",
            self.cache_file,
        )
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_get_cache_creates_file_when_missing(self):
        cache = GameInfoRepository.get_cache(TEST_LOGGER)
        self.assertEqual(cache, {})
        self.assertTrue(Path(self.cache_file).exists())

    def test_get_cache_does_not_write_when_dry_run(self):
        cache = GameInfoRepository.get_cache(TEST_LOGGER, dry_run=True)
        self.assertEqual(cache, {})
        self.assertFalse(Path(self.cache_file).exists())

    def test_get_cache_loads_existing_file(self):
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump({"123": {"game_id": "123", "name": "Hollow Knight"}}, f)
        cache = GameInfoRepository.get_cache(TEST_LOGGER)
        self.assertEqual(cache["123"], GameInfo("123", "Hollow Knight"))

    def test_get_cache_returns_empty_on_corrupted_file(self):
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            f.write("{ not json")
        cache = GameInfoRepository.get_cache(TEST_LOGGER)
        self.assertEqual(cache, {})

    def test_save_cache_writes_to_disk(self):
        GameInfoRepository.save_cache(
            {"123": GameInfo("123", "Hollow Knight")}, TEST_LOGGER, dry_run=False
        )
        with open(self.cache_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.assertEqual(raw["123"], {"game_id": "123", "name": "Hollow Knight"})

    def test_save_cache_does_not_write_when_dry_run(self):
        GameInfoRepository.save_cache(
            {"123": GameInfo("123", "Hollow Knight")}, TEST_LOGGER, dry_run=True
        )
        self.assertFalse(Path(self.cache_file).exists())
        self.assertEqual(
            GameInfoRepository._cache,  # pyright: ignore[reportPrivateUsage]
            {"123": GameInfo("123", "Hollow Knight")},
        )

    def test_from_cache_returns_none_for_unknown_game(self):
        self.assertIsNone(GameInfoRepository.from_cache("999", TEST_LOGGER))

    def test_from_cache_returns_matching_item(self):
        GameInfoRepository.save_cache(
            {"123": GameInfo("123", "Hollow Knight")}, TEST_LOGGER, dry_run=False
        )
        GameInfoRepository._cache = None  # pyright: ignore[reportPrivateUsage]
        result = GameInfoRepository.from_cache("123", TEST_LOGGER)
        self.assertEqual(result, GameInfo("123", "Hollow Knight"))

    def test_from_cache_does_not_create_file_when_dry_run(self):
        result = GameInfoRepository.from_cache("123", TEST_LOGGER, dry_run=True)
        self.assertIsNone(result)
        self.assertFalse(Path(self.cache_file).exists())

    def test_put_in_cache_adds_item_and_persists(self):
        GameInfoRepository.put_in_cache(
            GameInfo("456", "A Plague Tale"), TEST_LOGGER, dry_run=False
        )
        with open(self.cache_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.assertIn("456", raw)

    def test_put_in_cache_does_not_persist_when_dry_run(self):
        GameInfoRepository.put_in_cache(
            GameInfo("456", "A Plague Tale"), TEST_LOGGER, dry_run=True
        )
        self.assertFalse(Path(self.cache_file).exists())
        result = GameInfoRepository.from_cache("456", TEST_LOGGER)
        self.assertEqual(result, GameInfo("456", "A Plague Tale"))


if __name__ == "__main__":
    _ = unittest.main()
