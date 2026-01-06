"""Umu Launcher Feature Provider"""

from typing import override
from core.configuration_property import ConfigurationProperty
from core.configuration_types import ConfigurationDictionary
from core.feature_provider import FeatureProvider
from core.runtime_configuration import PipelineWrapper, RuntimeConfiguration

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
                PipelineWrapper(
                    f"{umu_binary} --",
                    is_global_wrapper=False,
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
