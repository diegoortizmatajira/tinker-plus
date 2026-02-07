"""Module providing SDL configuration features."""

from core import (
    ConfigurationProperty,
    FeatureProvider,
    ListItem,
)

SDL_VIDEODRIVER_PROPERTY = ConfigurationProperty(
    str,
    "SDL_VIDEODRIVER",
    "SDL Video Driver",
    "Simple DirectMedia Layer (SDL) video driver to use.",
    generated_environment_variable="SDL_VIDEODRIVER",
    values_provider=lambda _runtime_configuration, _logger: [
        ListItem("wayland", "wayland"),
        ListItem("wayland,x11,dummy", "wayland,x11,dummy"),
        ListItem("x11", "x11"),
        ListItem("x11,wayland,dummy", "x11,wayland,dummy"),
        ListItem("dummy", "dummy"),
    ],
)


class SdlConfig(FeatureProvider):
    """
    Provides SDL configuration features, specifically managing
    the SDL video driver property.

    This class is responsible for initializing and managing
    configuration properties related to SDL, such as the
    `SDL_VIDEODRIVER_PROPERTY`.
    """

    def __init__(self):
        super().__init__(
            "SDL Configuration",
            [
                SDL_VIDEODRIVER_PROPERTY,
            ],
            "General",
        )
