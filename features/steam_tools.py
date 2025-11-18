"""Feature provider for Steam tools and wrappers."""

from typing import override
from core.configuration_property import BINARY_PROPERTY, ConfigurationProperty
from core.feature_provider import FeatureProvider
from core.runtime_configuration import RuntimeConfiguration, PipelineWrapper

STEAM_USE_WRAPPER_PROPERTY = ConfigurationProperty(
    "STEAM_USE_WRAPPER",
    "Enables the use of Steam wrapper for Steam games when set to '1'.",
    default="0",
    type=BINARY_PROPERTY,
)

STEAM_USE_SNIPER_PROPERTY = ConfigurationProperty(
    "STEAM_USE_SNIPER",
    "Enables the use of Sniper for Steam games when set to '1'.",
    default="1",
    type=BINARY_PROPERTY,
)

STEAM_USE_REAPER_PROPERTY = ConfigurationProperty(
    "STEAM_USE_REAPER",
    "Enables the use of Reaper for Steam games when set to '1'.",
    default="1",
    type=BINARY_PROPERTY,
)


class SteamTools(FeatureProvider):
    """
    A feature provider for Steam tools that manages the application of
    configuration settings related to different Steam wrappers and tools.

    SteamTools enables the management of specific pipeline wrappers like
    Sniper, Reaper, and a general Steam wrapper based on configuration
    properties provided at runtime.
    """

    def __init__(self):
        super().__init__(
            [
                STEAM_USE_WRAPPER_PROPERTY,
                STEAM_USE_SNIPER_PROPERTY,
                STEAM_USE_REAPER_PROPERTY,
            ]
        )

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        # Apply the Steam wrapper
        if (
            STEAM_USE_WRAPPER_PROPERTY.get(configuration) == "1"
            and runtime_configuration.steam_wrapper
        ):
            runtime_configuration.add_pipeline_wrapper(
                PipelineWrapper(runtime_configuration.steam_wrapper)
            )
        # Apply the Sniper
        if (
            STEAM_USE_SNIPER_PROPERTY.get(configuration) == "1"
            and runtime_configuration.steam_sniper
        ):
            runtime_configuration.add_pipeline_wrapper(
                PipelineWrapper(runtime_configuration.steam_sniper)
            )
        # Apply the Reaper
        if (
            STEAM_USE_REAPER_PROPERTY.get(configuration) == "1"
            and runtime_configuration.steam_reaper
        ):
            runtime_configuration.add_pipeline_wrapper(
                PipelineWrapper(
                    wrapper=lambda cmd, runtime_configuration: (
                        f"{runtime_configuration.steam_reaper}"
                        f" SteamLaunch AppId={runtime_configuration.steam_app_id}"
                        f" -- {cmd}"
                    ),
                )
            )
        return runtime_configuration
