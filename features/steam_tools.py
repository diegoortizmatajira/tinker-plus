"""Feature provider for Steam tools and wrappers."""

from typing import override
from core.configuration_property import BINARY_PROPERTY, ConfigurationProperty
from core.feature_provider import FeatureProvider
from core.runtime_configuration import RuntimeConfiguration, PipelineWrapper

STEAM_USE_WRAPPER_PROPERTY = ConfigurationProperty(
    "STEAM_USE_WRAPPER",
    "Enables the use of Steam wrapper for Steam games when set to '1'.",
    default=False,
    type=BINARY_PROPERTY,
)

STEAM_USE_SNIPER_PROPERTY = ConfigurationProperty(
    "STEAM_USE_SNIPER",
    "Enables the use of Sniper for Steam games when set to '1'.",
    default=True,
    type=BINARY_PROPERTY,
)

STEAM_USE_REAPER_PROPERTY = ConfigurationProperty(
    "STEAM_USE_REAPER",
    "Enables the use of Reaper for Steam games when set to '1'.",
    default=True,
    type=BINARY_PROPERTY,
)

STEAM_LAST_WRAPPER_COMMAND_PROPERTY = ConfigurationProperty(
    "STEAM_LAST_WRAPPER_COMMAND",
    "Stores the last wrapper command used for Steam games.",
)

STEAM_LAST_REAPER_COMMAND_PROPERTY = ConfigurationProperty(
    "STEAM_LAST_REAPER_COMMAND",
    "Stores the last Reaper command used for Steam games.",
)

STEAM_LAST_SNIPER_COMMAND_PROPERTY = ConfigurationProperty(
    "STEAM_LAST_SNIPER_COMMAND",
    "Stores the last Sniper command used for Steam games.",
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
                STEAM_LAST_WRAPPER_COMMAND_PROPERTY,
                STEAM_LAST_SNIPER_COMMAND_PROPERTY,
                STEAM_LAST_REAPER_COMMAND_PROPERTY,
            ]
        )

    @override
    def build_configuration(
        self,
        sourced_configuration: dict,
        runtime_configuration: RuntimeConfiguration,
    ) -> dict:
        super().build_configuration(sourced_configuration, runtime_configuration)
        if runtime_configuration.steam_reaper:
            STEAM_LAST_WRAPPER_COMMAND_PROPERTY.set(
                sourced_configuration, runtime_configuration.steam_wrapper
            )
        if runtime_configuration.steam_sniper:
            STEAM_LAST_SNIPER_COMMAND_PROPERTY.set(
                sourced_configuration, runtime_configuration.steam_sniper
            )
        if runtime_configuration.steam_reaper:
            STEAM_LAST_REAPER_COMMAND_PROPERTY.set(
                sourced_configuration, runtime_configuration.steam_reaper
            )
        return sourced_configuration

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        # Load last used commands if not already set
        if not runtime_configuration.steam_wrapper:
            runtime_configuration.steam_wrapper = (
                STEAM_LAST_WRAPPER_COMMAND_PROPERTY.get_string(configuration)
            )
            self.logger.info(
                "Restored last used Steam wrapper command as it was not set by runtime provider."
            )
        self.logger.info(
            "Steam Launch Wrapper: %s", runtime_configuration.steam_wrapper
        )
        if not runtime_configuration.steam_sniper:
            runtime_configuration.steam_sniper = (
                STEAM_LAST_SNIPER_COMMAND_PROPERTY.get_string(configuration)
            )
            self.logger.info(
                "Restored last used Steam Sniper command as it was not set by runtime provider."
            )
        self.logger.info("Steam Sniper Command: %s", runtime_configuration.steam_sniper)
        if not runtime_configuration.steam_reaper:
            runtime_configuration.steam_reaper = (
                STEAM_LAST_REAPER_COMMAND_PROPERTY.get_string(configuration)
            )
            self.logger.info(
                "Restored last used Steam Reaper command as it was not set by runtime provider."
            )
        self.logger.info("Steam Reaper Command: %s", runtime_configuration.steam_reaper)
        # Apply the Steam wrapper
        if (
            STEAM_USE_WRAPPER_PROPERTY.get_boolean(configuration)
            and runtime_configuration.steam_wrapper
        ):
            self.logger.info("Enabling Steam wrapper.")
            runtime_configuration.add_pipeline_wrapper(
                PipelineWrapper(
                    runtime_configuration.steam_wrapper,
                    is_global_wrapper=True,
                )
            )
        # Apply the Sniper
        if (
            STEAM_USE_SNIPER_PROPERTY.get_boolean(configuration)
            and runtime_configuration.steam_sniper
        ):
            self.logger.info("Enabling Steam Sniper wrapper.")
            runtime_configuration.add_pipeline_wrapper(
                PipelineWrapper(
                    runtime_configuration.steam_sniper.replace(
                        "waitforexitandrun", "run"
                    ),
                    is_global_wrapper=True,
                )
            )
        # Apply the Reaper
        if (
            STEAM_USE_REAPER_PROPERTY.get_boolean(configuration)
            and runtime_configuration.steam_reaper
        ):
            self.logger.info("Enabling Steam Reaper wrapper.")
            runtime_configuration.add_pipeline_wrapper(
                PipelineWrapper(
                    f"{runtime_configuration.steam_reaper} --",
                    is_global_wrapper=True,
                )
            )
        return runtime_configuration
