"""Module to manage external tools being used when running the game."""

from typing import override
from core.configuration_property import ConfigurationProperty
from core.feature_provider import FeatureProvider
from core.runtime_configuration import (
    ExecutableCommand,
    PipelineWrapper,
    RuntimeConfiguration,
)

GAMEMODERUN_ENABLED_PROPERTY = ConfigurationProperty(
    bool,
    "GAMEMODERUN_ENABLED",
    "Enables GameModeRun when set to 'True'.",
    default=False,
)

GAMESCOPE_ENABLED_PROPERTY = ConfigurationProperty(
    bool,
    "GAMESCOPE_ENABLED",
    "Enables Gamescope when set to 'True'.",
    default=False,
)
GAMESCOPE_ARGS_PROPERTY = ConfigurationProperty(
    str,
    "GAMESCOPE_ARGS",
    "Additional arguments to pass to Gamescope.",
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
        if GAMEMODERUN_ENABLED_PROPERTY.get(configuration):
            self.logger.info("Enabling GameModeRun wrapper.")
            runtime_configuration.add_pipeline_wrapper(PipelineWrapper("gamemoderun"))
        if GAMESCOPE_ENABLED_PROPERTY.get(configuration):
            gamescope_args = GAMESCOPE_ARGS_PROPERTY.get(configuration) or ""
            self.logger.info(
                'Enabling Gamescope wrapper with args: "%s"', gamescope_args
            )
            command = ExecutableCommand("gamescope", args=gamescope_args)
            runtime_configuration.add_pipeline_wrapper(
                PipelineWrapper(
                    wrapper=lambda cmd, _: (f"{command.get_full_command()} -- {cmd}"),
                )
            )
        return runtime_configuration
