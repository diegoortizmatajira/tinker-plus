"""Module providing SDL configuration features."""

from core.configuration_property import (
    LIST_PROPERTY,
    ConfigurationProperty,
    ListItem,
)
from core.feature_provider import FeatureProvider

SDL_VIDEODRIVER_PROPERTY = ConfigurationProperty(
    "SDL_VIDEODRIVER",
    "Simple DirectMedia Layer (SDL) video driver to use.",
    type=LIST_PROPERTY,
    generated_environment_variable="SDL_VIDEODRIVER",
    values_provider=lambda _: [
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
            [
                SDL_VIDEODRIVER_PROPERTY,
            ]
        )
