"""Feature provider for Wine configuration."""

from core.configuration_property import ConfigurationProperty
from core.feature_provider import FeatureProvider

WINE_DLLOVERRIDES_PROPERTY = ConfigurationProperty(
    str,
    "WINE_DLLOVERRIDES",
    "Specifies custom DLL overrides for Wine. The value should be"
    " a semicolon-separated list of DLL names and their override"
    " settings (e.g., 'dll1,native;dll2,builtin').",
    generated_environment_variable="WINEDLLOVERRIDES",
)


class WineConfig(FeatureProvider):
    """Provides Wine configuration features, including custom DLL overrides."""

    def __init__(self):
        super().__init__(
            "Wine Configuration",
            [
                WINE_DLLOVERRIDES_PROPERTY,
            ],
            "General",
        )
