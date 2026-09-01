import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.config_storage import ConfigStorage
from model import GameInfo


class TestConfigStorage(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.tmp_dir, ignore_errors=True))
        self.config_location = str(self.tmp_dir / "config")
        self.global_config_file = str(self.tmp_dir / "config" / "global_config.json")
        self.game_config_dir = str(self.tmp_dir / "config" / "game_configs")
        self.game_config_file_template = f"{self.game_config_dir}/{{}}.json"

        patches = [
            patch("core.config_storage.CONFIG_LOCATION", self.config_location),
            patch("core.config_storage.GLOBAL_CONFIG_FILE", self.global_config_file),
            patch("core.config_storage.GAME_CONFIG_DIR", self.game_config_dir),
            patch(
                "core.config_storage.GAME_CONFIG_FILE_TEMPLATE",
                self.game_config_file_template,
            ),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.storage = ConfigStorage()

    def test_get_game_configuration_files_empty_when_dir_missing(self):
        self.assertEqual(self.storage.get_game_configuration_files(), [])

    def test_get_game_configuration_files_lists_json_files(self):
        Path(self.game_config_dir).mkdir(parents=True)
        (Path(self.game_config_dir) / "123.json").write_text("{}")
        (Path(self.game_config_dir) / "notes.txt").write_text("ignored")
        files = self.storage.get_game_configuration_files()
        self.assertEqual([f.name for f in files], ["123.json"])

    def test_get_global_config_returns_none_when_missing(self):
        self.assertIsNone(self.storage.get_global_config())

    def test_save_and_get_global_config_round_trip(self):
        self.storage.save_global_config({"KEY": "value"})
        self.assertEqual(self.storage.get_global_config(), {"KEY": "value"})

    def test_save_global_config_does_not_write_when_dry_run(self):
        self.storage.save_global_config({"KEY": "value"}, dry_run=True)
        self.assertFalse(Path(self.global_config_file).exists())

    def test_save_game_config_does_not_write_when_dry_run(self):
        self.storage.save_game_config({"KEY": "value"}, "123", None, dry_run=True)
        self.assertFalse(Path(self.game_config_file_template.format("123")).exists())

    def test_save_and_get_game_config_round_trip(self):
        self.storage.save_game_config({"KEY": "value"}, "123", None)
        self.assertEqual(self.storage.get_game_config("123"), {"KEY": "value"})

    def test_save_game_config_persists_only_the_diff_from_global(self):
        global_config = {"SHARED": "same", "OVERRIDDEN": "global_value"}
        game_config = {"SHARED": "same", "OVERRIDDEN": "game_value", "ONLY_GAME": "x"}
        self.storage.save_game_config(game_config, "123", global_config)
        saved = self.storage.get_game_config("123")
        self.assertEqual(
            saved, {"OVERRIDDEN": "game_value", "ONLY_GAME": "x"}
        )

    def test_build_global_configuration_merges_with_stored_config(self):
        self.storage.save_global_config({"EXISTING": "stored"})
        result = self.storage.build_global_configuration({"NEW_DEFAULT": "default"})
        self.assertEqual(result["EXISTING"], "stored")
        self.assertEqual(result["NEW_DEFAULT"], "default")

    def test_build_global_configuration_persists_result(self):
        self.storage.build_global_configuration({"NEW_DEFAULT": "default"})
        self.assertEqual(
            self.storage.get_global_config(), {"NEW_DEFAULT": "default"}
        )

    def test_build_global_configuration_dry_run_does_not_persist(self):
        self.storage.build_global_configuration({"NEW_DEFAULT": "default"}, dry_run=True)
        self.assertIsNone(self.storage.get_global_config())

    def test_build_global_configuration_clone_leaves_source_untouched(self):
        source = {"NEW_DEFAULT": "default"}
        self.storage.save_global_config({"EXISTING": "stored"})
        self.storage.build_global_configuration(source, clone_configuration=True)
        self.assertEqual(source, {"NEW_DEFAULT": "default"})

    def test_build_game_configuration_creates_file_when_none_exists(self):
        game_info = GameInfo("123", "Hollow Knight")
        result = self.storage.build_game_configuration(
            game_info, {"DEFAULT_KEY": "value"}, {"DEFAULT_KEY": "value"}
        )
        self.assertEqual(result["DEFAULT_KEY"], "value")
        self.assertTrue(Path(self.game_config_file_template.format("123")).exists())

    def test_build_game_configuration_dry_run_does_not_create_file(self):
        game_info = GameInfo("123", "Hollow Knight")
        self.storage.build_game_configuration(
            game_info, {"DEFAULT_KEY": "value"}, {}, dry_run=True
        )
        self.assertFalse(Path(self.game_config_file_template.format("123")).exists())

    def test_build_game_configuration_does_not_resave_when_config_exists(self):
        game_info = GameInfo("123", "Hollow Knight")
        self.storage.save_game_config({"STORED": "value"}, "123", None)
        mtime_before = Path(self.game_config_file_template.format("123")).stat().st_mtime
        result = self.storage.build_game_configuration(game_info, {}, {})
        self.assertEqual(result["STORED"], "value")
        mtime_after = Path(self.game_config_file_template.format("123")).stat().st_mtime
        self.assertEqual(mtime_before, mtime_after)

    def test_validate_config_reports_unexpected_keys(self):
        from core.feature_provider import FeatureProvider
        from model import ConfigurationProperty

        class DummyFeature(FeatureProvider):
            def __init__(self):
                super().__init__(
                    "Dummy", [ConfigurationProperty(str, "EXPECTED_KEY", "x", "x")]
                )

        game_info = GameInfo("123", "Hollow Knight")
        self.storage.save_game_config(
            {"EXPECTED_KEY": "value", "UNEXPECTED_KEY": "value"}, "123", None
        )
        errors = self.storage.validate_config(game_info, [DummyFeature()], dry_run=True)
        self.assertEqual(errors, ["Unexpected config key: UNEXPECTED_KEY"])

    def test_validate_config_dry_run_does_not_change_stored_file(self):
        from core.feature_provider import FeatureProvider

        class DummyFeature(FeatureProvider):
            def __init__(self):
                super().__init__("Dummy", [])

        game_info = GameInfo("123", "Hollow Knight")
        self.storage.save_game_config({"EXISTING": "value"}, "123", None)
        content_before = Path(self.game_config_file_template.format("123")).read_text()
        _ = self.storage.validate_config(game_info, [DummyFeature()], dry_run=True)
        content_after = Path(self.game_config_file_template.format("123")).read_text()
        self.assertEqual(json.loads(content_before), json.loads(content_after))


if __name__ == "__main__":
    _ = unittest.main()
