import unittest

from features.gui_options import GuiOptions
from model import RuntimeConfiguration


class TestGuiOptionsInit(unittest.TestCase):
    def test_defaults_before_apply_configuration(self):
        feature = GuiOptions()
        self.assertTrue(feature.use_ui)
        self.assertTrue(feature.close_after_running_game)
        self.assertEqual(feature.autorun_timeout, 3)


class TestGuiOptionsApplyConfiguration(unittest.TestCase):
    def setUp(self):
        self.feature = GuiOptions()
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_caches_values_from_configuration(self):
        self.feature.apply_configuration(
            {
                "GUI_SHOW_UI": False,
                "GUI_CLOSE_AFTER_RUNNING_GAME": False,
                "GUI_AUTORUN_TIMEOUT": 10,
            },
            self.runtime_configuration,
        )
        self.assertFalse(self.feature.use_ui)
        self.assertFalse(self.feature.close_after_running_game)
        self.assertEqual(self.feature.autorun_timeout, 10)

    def test_applies_defaults_when_configuration_empty(self):
        self.feature.apply_configuration({}, self.runtime_configuration)
        self.assertTrue(self.feature.use_ui)
        self.assertTrue(self.feature.close_after_running_game)
        self.assertEqual(self.feature.autorun_timeout, 3)

    def test_returns_the_runtime_configuration_unchanged(self):
        result = self.feature.apply_configuration({}, self.runtime_configuration)
        self.assertIs(result, self.runtime_configuration)

    def test_raises_keyerror_when_show_ui_explicitly_none(self):
        with self.assertRaises(KeyError):
            self.feature.apply_configuration(
                {"GUI_SHOW_UI": None}, self.runtime_configuration
            )

    def test_raises_keyerror_when_close_after_running_game_explicitly_none(self):
        with self.assertRaises(KeyError):
            self.feature.apply_configuration(
                {"GUI_CLOSE_AFTER_RUNNING_GAME": None}, self.runtime_configuration
            )

    def test_raises_keyerror_when_autorun_timeout_explicitly_none(self):
        with self.assertRaises(KeyError):
            self.feature.apply_configuration(
                {"GUI_AUTORUN_TIMEOUT": None}, self.runtime_configuration
            )


if __name__ == "__main__":
    _ = unittest.main()
