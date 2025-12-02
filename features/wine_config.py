"""Feature provider for Wine configuration."""

from core.configuration_property import ConfigurationProperty, ListItem
from core.feature_provider import FeatureProvider

WINE_DLLOVERRIDES_PROPERTY = ConfigurationProperty(
    str,
    "WINE_DLLOVERRIDES",
    "Wine DLL Overrides",
    "Specifies custom DLL overrides for Wine. The value should be"
    " a semicolon-separated list of DLL names and their override"
    " settings (e.g., 'dll1,native;dll2,builtin').",
    generated_environment_variable="WINEDLLOVERRIDES",
)

WINE_FULLSCREEN_FSR_PROPERTY = ConfigurationProperty(
    bool,
    "WINE_FULLSCREEN_FSR_MODE",
    "Enable Fullscreen FSR Mode",
    "Enables Fullscreen FSR (FidelityFX Super Resolution) mode in Wine",
    generated_environment_variable="WINE_FULLSCREEN_FSR_MODE",
)

WINE_FULLSCREEN_FSR_MODE = ConfigurationProperty(
    str,
    "WINE_FULLSCREEN_FSR_MODE",
    "Fullscreen FSR Mode",
    "Sets the Fullscreen FSR mode for Wine.",
    generated_environment_variable="WINE_FULLSCREEN_FSR_MODE",
    values_provider=lambda *_: [
        ListItem("ultra", "ultra"),
        ListItem("quality", "quality"),
        ListItem("balanced", "balanced"),
        ListItem("performance", "performance"),
    ],
)

WINE_FULLSCREEN_FSR_CUSTOM_MODE_PROPERTY = ConfigurationProperty(
    str,
    "WINE_FULLSCREEN_FSR_CUSTOM_MODE",
    "Custom Fullscreen FSR Mode",
    "Sets a custom Fullscreen FSR mode for Wine when 'custom' is selected"
    " in the Fullscreen FSR Mode setting. The value should be a"
    " resolution scale factor (e.g., '1.5' for 150% scaling).",
    generated_environment_variable="WINE_FULLSCREEN_FSR_CUSTOM_MODE",
)


class WineConfig(FeatureProvider):
    """Provides Wine configuration features, including custom DLL overrides."""

    def __init__(self):
        super().__init__(
            "Wine Configuration",
            [
                WINE_DLLOVERRIDES_PROPERTY,
                WINE_FULLSCREEN_FSR_PROPERTY,
                WINE_FULLSCREEN_FSR_MODE,
                WINE_FULLSCREEN_FSR_CUSTOM_MODE_PROPERTY,
            ],
            "General",
        )
