"""General runtime feature provider."""

from typing import override
from core.configuration_property import ConfigurationProperty
from core.feature_provider import FeatureProvider
from core.runtime_configuration import RuntimeConfiguration

GENERAL_LOG_INDIVIDUAL_EXE_PROPERTY = ConfigurationProperty(
    bool,
    "GENERAL_LOG_INDIVIDUAL_EXE",
    "Log Individual Executables",
    "If set to True, logs each individual executable that is run in is own file.",
    default=False,
)

class GeneralRuntime(FeatureProvider):
    """
    A feature provider that applies general runtime configurations.

    This class manages the integration of generic runtime settings,
    particularly for logging executable commands, by interacting
    with configuration properties.
    """

    def __init__(self):
        super().__init__(
            "General Runtime",
            [
                GENERAL_LOG_INDIVIDUAL_EXE_PROPERTY,
            ],
            "General",
        )

    @override
    def apply_configuration(
        self, _configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        runtime_configuration.log_executable_commands = (
            GENERAL_LOG_INDIVIDUAL_EXE_PROPERTY.get(_configuration, False)
        )
        self.logger.info(
            "Individual executable logging is set to: %s",
            runtime_configuration.log_executable_commands,
        )
        return runtime_configuration
