"""Module providing SDL configuration features."""

from core.configuration_property import (
    LIST_PROPERTY,
    MULTIVALUELIST_PROPERTY,
    ConfigurationProperty,
    ListItem,
)
from core.feature_provider import FeatureProvider


SDL_VIDEODRIVER_PROPERTY = ConfigurationProperty(
    "SDL_VIDEODRIVER",
    "Simple DirectMedia Layer (SDL2) video driver to use.",
    type=LIST_PROPERTY,
    generated_environment_variable="SDL_VIDEODRIVER",
    values_provider=lambda _: [
        ListItem("x11", "x11"),
        ListItem("wayland", "wayland"),
        ListItem("dummy", "dummy"),
    ],
)
SDL_HINT_VIDEO_DRIVER_PROPERTY = ConfigurationProperty(
    "SDL_HINT_VIDEO_DRIVER",
    "Simple DirectMedia Layer (SDL3) hint for video driver to use.",
    generated_environment_variable="SDL_HINT_VIDEO_DRIVER",
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
            [
                SDL_VIDEODRIVER_PROPERTY,
                SDL_HINT_VIDEO_DRIVER_PROPERTY,
            ]
        )
