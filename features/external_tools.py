"""Module to manage external tools being used when running the game."""

from typing import override
from core.configuration_property import (
    BINARY_PROPERTY,
    TEXT_PROPERTY,
    ConfigurationProperty,
)
from core.feature_provider import FeatureProvider
from core.runtime_configuration import (
    ExecutableCommand,
    PipelineWrapper,
    RuntimeConfiguration,
)

GAMEMODERUN_ENABLED_PROPERTY = ConfigurationProperty(
    "GAMEMODERUN_ENABLED",
    "Enables GameModeRun when set to '1'.",
    default=False,
    type=BINARY_PROPERTY,
)

GAMESCOPE_ENABLED_PROPERTY = ConfigurationProperty(
    "GAMESCOPE_ENABLED",
    "Enables Gamescope when set to '1'.",
    default=False,
    type=BINARY_PROPERTY,
)
GAMESCOPE_ARGS_PROPERTY = ConfigurationProperty(
    "GAMESCOPE_ARGS",
    "Additional arguments to pass to Gamescope.",
    type=TEXT_PROPERTY,
)


class ExternalTools(FeatureProvider):
    """
    A feature provider for managing external tools configuration.

    ExternalTools enables the configuration of properties related to external
    utilities such as GameModeRun and Gamescope. This class applies the
    specified configuration to the runtime environment by enabling or disabling
    respective tools based on the configuration values.
    """

    def __init__(self):
        super().__init__(
            [
                GAMEMODERUN_ENABLED_PROPERTY,
                GAMESCOPE_ENABLED_PROPERTY,
                GAMESCOPE_ARGS_PROPERTY,
            ]
        )

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        if GAMEMODERUN_ENABLED_PROPERTY.get_boolean(configuration):
            self.logger.info("Enabling GameModeRun wrapper.")
            runtime_configuration.add_pipeline_wrapper(
                PipelineWrapper("gamemoderun", applies_to_forks=False)
            )
        if GAMESCOPE_ENABLED_PROPERTY.get_boolean(configuration):
            gamescope_args = GAMESCOPE_ARGS_PROPERTY.get_string(configuration) or ""
            self.logger.info(
                'Enabling Gamescope wrapper with args: "%s"', gamescope_args
            )
            command = ExecutableCommand("gamescope", args=gamescope_args)
            runtime_configuration.add_pipeline_wrapper(
                PipelineWrapper(
                    wrapper=lambda cmd, *_: (f"{command.get_full_command()} -- {cmd}"),
                    applies_to_forks=False,
                )
            )
        return runtime_configuration
