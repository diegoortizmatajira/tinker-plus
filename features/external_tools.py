"""Module to manage external tools being used when running the game."""

from typing import override
from core import FeatureProvider
from model import (
    Command,
    ConfigurationProperty,
    CommandWrapper,
    ConfigurationDictionary,
    RuntimeConfiguration,
)

EXTERNAL_TERMINAL_COMMAND_TEMPLATE_PROPERTY = ConfigurationProperty(
    list,
    "EXTERNAL_TERMINAL_COMMAND_TEMPLATE",
    "External Terminal Command Template",
    (
        "Template for launching a command in an external terminal."
        "Use {command} for the launch command."
    ),
    default=["ghostty", "-e", "/bin/bash", "-c", "{command} && sleep 5"],
)
GAMEMODERUN_ENABLED_PROPERTY = ConfigurationProperty(
    bool,
    "GAMEMODERUN_ENABLED",
    "Enable GameModeRun",
    "Enables GameModeRun when set to 'True'.",
    default=False,
)

GAMESCOPE_ENABLED_PROPERTY = ConfigurationProperty(
    bool,
    "GAMESCOPE_ENABLED",
    "Enable Gamescope",
    "Enables Gamescope when set to 'True'.",
    default=False,
)
GAMESCOPE_ARGS_PROPERTY = ConfigurationProperty(
    str,
    "GAMESCOPE_ARGS",
    "Gamescope Arguments",
    "Additional arguments to pass to Gamescope.",
)

MANGOHUD_ENABLED_PROPERTY = ConfigurationProperty(
    bool,
    "MANGOHUD_ENABLED",
    "Enable MangoHUD",
    "Enables MangoHUD when set to 'True'.",
    default=False,
)
MANGOHUG_CONFIG_PROPERTY = ConfigurationProperty(
    str,
    "MANGOHUD_CONFIG",
    "MangoHUD Configuration",
    "Configuration string for MangoHUD.",
    generated_environment_variable="MANGOHUD_CONFIG",
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
            "Run in the pipeline",
            [
                GAMEMODERUN_ENABLED_PROPERTY,
                GAMESCOPE_ENABLED_PROPERTY,
                GAMESCOPE_ARGS_PROPERTY,
                MANGOHUD_ENABLED_PROPERTY,
                MANGOHUG_CONFIG_PROPERTY,
                EXTERNAL_TERMINAL_COMMAND_TEMPLATE_PROPERTY,
            ],
            "Additional Tools",
        )

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        if GAMEMODERUN_ENABLED_PROPERTY.get(configuration):
            self.logger.info("Enabling GameModeRun wrapper.")
            runtime_configuration.add_pipeline_wrapper(CommandWrapper("gamemoderun"))
        if GAMESCOPE_ENABLED_PROPERTY.get(configuration):
            gamescope_args = GAMESCOPE_ARGS_PROPERTY.get(configuration) or ""
            self.logger.info(
                'Enabling Gamescope wrapper with args: "%s"', gamescope_args
            )
            command = Command("gamescope", args=gamescope_args)
            runtime_configuration.add_pipeline_wrapper(
                CommandWrapper(
                    wrapper=lambda cmd, _: (f"{command.get_full_command()} -- {cmd}"),
                )
            )
        if MANGOHUD_ENABLED_PROPERTY.get(configuration):
            self.logger.info("Enabling MangoHUD wrapper.")
            runtime_configuration.add_pipeline_wrapper(CommandWrapper("mangohud"))

        runtime_configuration.external_terminal_command_template = (
            EXTERNAL_TERMINAL_COMMAND_TEMPLATE_PROPERTY.get(configuration) or []
        )
        self.logger.info(
            "Configured external terminal command template: '%s'",
            " ".join(runtime_configuration.external_terminal_command_template),
        )
        return runtime_configuration
