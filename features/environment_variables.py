from typing import override
from core import ConfigurationProperty, FeatureProvider, RuntimeConfiguration
from core.configuration_types import ConfigurationDictionary


ENVIRONMENT_VARIABLES = ConfigurationProperty(
    list,
    "ENVIRONMENT_VARIABLES",
    "List of additional environment variables",
    "A list of additional environment variables to set for the game process. Each entry should be in the format 'KEY=VALUE'.",
)


class EnvironmentVariables(FeatureProvider):
    """Feature provider for backing up and restoring game files.

    This class facilitates the process of backing up game files to a specified location
    and restoring them from that location. It defines actions for both backup and
    restoration, leveraging provided runtime configurations and commands.
    """

    def __init__(self):
        super().__init__(
            "Environment Variables",
            [
                ENVIRONMENT_VARIABLES,
            ],
            "Game Execution",
        )

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        env_vars: list[str] = ENVIRONMENT_VARIABLES.get(configuration, [])
        for var in env_vars:
            key_value = var.split("=", 1)
            if len(key_value) == 2:
                key, value = key_value
                self.logger.info(f"Setting environment variable: {key}={value}")
                runtime_configuration.set_environment_variable(key, value)
        return runtime_configuration
