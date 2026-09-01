import unittest

from features.sdl_config import SDL_VIDEODRIVER_PROPERTY, SdlConfig
from model import RuntimeConfiguration


class TestSdlConfig(unittest.TestCase):
    def test_registers_sdl_videodriver_property(self):
        feature = SdlConfig()
        self.assertEqual(feature.name, "SDL Configuration")
        self.assertEqual(feature.category, "General")
        self.assertEqual(list(feature.properties), [SDL_VIDEODRIVER_PROPERTY])

    def test_generated_environment_variable_is_set(self):
        self.assertEqual(
            SDL_VIDEODRIVER_PROPERTY.generated_environment_variable, "SDL_VIDEODRIVER"
        )

    def test_videodriver_values_provider_returns_expected_options(self):
        runtime_configuration = RuntimeConfiguration.empty()
        values = SDL_VIDEODRIVER_PROPERTY.get_possible_values(
            runtime_configuration, SdlConfig().logger
        )
        assert values is not None
        self.assertEqual(
            [item.value for item in values],
            ["wayland", "wayland,x11,dummy", "x11", "x11,wayland,dummy", "dummy"],
        )


if __name__ == "__main__":
    _ = unittest.main()
