"""Umu Launcher Feature Provider"""

from typing import override
from core import ConfigurationProperty, FeatureProvider
from model import (
    CommandCategory,
    CommandWrapper,
    RuntimeConfiguration,
    ConfigurationDictionary,
)

UMU_RUN_ENABLED_PROPERTY = ConfigurationProperty(
    bool,
    "UMU_RUN_ENABLED",
    "Enable Umu runner",
    "Enables the Umu runner for supported applications when set to 'True'.",
    default=False,
)
UMU_RUN_BINARY_PROPERTY = ConfigurationProperty(
    str,
    "UMU_RUN_BINARY",
    "'umu-run' Binary Path",
    "Specifies the file path to the Umu Launcher executable.",
    default="umu-run",
)

UMU_RUN_USE_STEAM_PREFIX_PROPERTY = ConfigurationProperty(
    bool,
    "UMU_RUN_USE_STEAM_PREFIX",
    "Use Steam Prefix",
    "If enabled, Umu will utilize the Steam prefix for launching games.",
    default=True,
)


class UmuRunner(FeatureProvider):
    """
    Feature Provider for Umu Launcher integration.
    """

    def __init__(self):
        super().__init__(
            "Steam Tools",
            [
                UMU_RUN_ENABLED_PROPERTY,
                UMU_RUN_BINARY_PROPERTY,
                UMU_RUN_USE_STEAM_PREFIX_PROPERTY,
            ],
            "Pipeline",
        )

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        # Apply the Sniper (After Reaper)
        umu_binary = UMU_RUN_BINARY_PROPERTY.get(configuration)
        if UMU_RUN_ENABLED_PROPERTY.get(configuration) and umu_binary:
            self.logger.info("Enabling Umu Runner.")
            runtime_configuration.add_pipeline_wrapper(
                CommandWrapper(
                    f"{umu_binary} --",
                    applies_for=[
                        CommandCategory.GAME,
                        CommandCategory.COMPATIBILITY_TOOL,
                    ],
                )
            )
        return runtime_configuration

    @override
    def before_execution(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        """
        Maps the required environment variables before execution.
        """
        umu_binary = UMU_RUN_BINARY_PROPERTY.get(configuration)
        if UMU_RUN_ENABLED_PROPERTY.get(configuration) and umu_binary:
            self.logger.info("Setting Umu environment variables.")
            runtime_configuration.set_environment_variable(
                "WINEPREFIX", runtime_configuration.prefix_path or "."
            )
