import json
import logging
import unittest
from pathlib import Path
from unittest.mock import patch

from model import CompatToolInfo, RuntimeConfiguration
from repositories.compat_tool_info_repository import CompatToolInfoRepository

TEST_LOGGER = logging.getLogger("test")


class TestCompatToolInfoRepository(unittest.TestCase):
    def setUp(self):
        CompatToolInfoRepository._cache = None  # pyright: ignore[reportPrivateUsage]
        self.tmp_dir = self._make_tmp_dir()
        self.cache_file = str(self.tmp_dir / "compat_tool_cache.json")
        self.patcher = patch(
            "repositories.compat_tool_info_repository.GLOBAL_COMPAT_TOOL_CACHE_FILE",
            self.cache_file,
        )
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def _make_tmp_dir(self) -> Path:
        import tempfile

        tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp_dir, ignore_errors=True))
        return tmp_dir

    def test_get_cache_creates_file_when_missing(self):
        self.assertFalse(Path(self.cache_file).exists())
        cache = CompatToolInfoRepository.get_cache(TEST_LOGGER)
        self.assertEqual(cache, {})
        self.assertTrue(Path(self.cache_file).exists())

    def test_get_cache_does_not_write_when_dry_run(self):
        CompatToolInfoRepository._cache = None  # pyright: ignore[reportPrivateUsage]
        cache = CompatToolInfoRepository.get_cache(TEST_LOGGER, dry_run=True)
        self.assertEqual(cache, {})
        self.assertFalse(Path(self.cache_file).exists())

    def test_get_cache_loads_existing_file(self):
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump({"Proton-8.0": {"name": "Proton-8.0", "dir": "/tools"}}, f)
        cache = CompatToolInfoRepository.get_cache(TEST_LOGGER)
        self.assertEqual(cache["Proton-8.0"], CompatToolInfo("Proton-8.0", "/tools"))

    def test_get_cache_returns_empty_on_corrupted_file(self):
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            f.write("not valid json {")
        cache = CompatToolInfoRepository.get_cache(TEST_LOGGER)
        self.assertEqual(cache, {})

    def test_save_cache_writes_to_disk(self):
        CompatToolInfoRepository.save_cache(
            {"Proton-8.0": CompatToolInfo("Proton-8.0", "/tools")},
            TEST_LOGGER,
            dry_run=False,
        )
        with open(self.cache_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.assertEqual(raw["Proton-8.0"], {"name": "Proton-8.0", "dir": "/tools"})

    def test_save_cache_does_not_write_when_dry_run(self):
        CompatToolInfoRepository.save_cache(
            {"Proton-8.0": CompatToolInfo("Proton-8.0", "/tools")},
            TEST_LOGGER,
            dry_run=True,
        )
        self.assertFalse(Path(self.cache_file).exists())
        # In-memory cache is still updated even when not persisted.
        self.assertEqual(
            CompatToolInfoRepository._cache,  # pyright: ignore[reportPrivateUsage]
            {"Proton-8.0": CompatToolInfo("Proton-8.0", "/tools")},
        )

    def test_from_cache_returns_none_for_unknown_name(self):
        self.assertIsNone(CompatToolInfoRepository.from_cache("missing", TEST_LOGGER))

    def test_from_cache_returns_matching_item(self):
        CompatToolInfoRepository.save_cache(
            {"Proton-8.0": CompatToolInfo("Proton-8.0", "/tools")},
            TEST_LOGGER,
            dry_run=False,
        )
        CompatToolInfoRepository._cache = None  # pyright: ignore[reportPrivateUsage]
        result = CompatToolInfoRepository.from_cache("Proton-8.0", TEST_LOGGER)
        self.assertEqual(result, CompatToolInfo("Proton-8.0", "/tools"))

    def test_from_cache_does_not_create_file_when_dry_run(self):
        result = CompatToolInfoRepository.from_cache(
            "anything", TEST_LOGGER, dry_run=True
        )
        self.assertIsNone(result)
        self.assertFalse(Path(self.cache_file).exists())

    def test_put_in_cache_adds_item_and_persists(self):
        CompatToolInfoRepository.put_in_cache(
            CompatToolInfo("Proton-9.0", "/tools9"), TEST_LOGGER, dry_run=False
        )
        with open(self.cache_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.assertIn("Proton-9.0", raw)

    def test_put_in_cache_does_not_persist_when_dry_run(self):
        CompatToolInfoRepository.put_in_cache(
            CompatToolInfo("Proton-9.0", "/tools9"), TEST_LOGGER, dry_run=True
        )
        self.assertFalse(Path(self.cache_file).exists())
        result = CompatToolInfoRepository.from_cache("Proton-9.0", TEST_LOGGER)
        self.assertEqual(result, CompatToolInfo("Proton-9.0", "/tools9"))

    def test_scan_and_populate_cache_finds_proton_folders(self):
        tools_dir = self.tmp_dir / "compat_tools"
        (tools_dir / "GE-Proton10-25").mkdir(parents=True)
        (tools_dir / "not_a_tool").mkdir(parents=True)
        configuration = RuntimeConfiguration.empty()
        configuration.steam_environment_data.steam_base_folder = str(
            self.tmp_dir / "nonexistent_steam"
        )
        configuration.steam_compatibility_tools_path = str(tools_dir)

        result = CompatToolInfoRepository.scan_and_populate_cache(
            TEST_LOGGER, configuration, dry_run=True
        )
        self.assertIn("GE-Proton10-25", result)
        self.assertNotIn("not_a_tool", result)
        self.assertEqual(result["GE-Proton10-25"].dir, str(tools_dir))


if __name__ == "__main__":
    _ = unittest.main()
