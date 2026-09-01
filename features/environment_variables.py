"""Module providing the custom environment variables feature."""

from typing import override

from core import FeatureProvider
from model import ConfigurationProperty, ConfigurationDictionary, RuntimeConfiguration

ENVIRONMENT_VARIABLES = ConfigurationProperty(
    list,
    "ENVIRONMENT_VARIABLES",
    "List of additional environment variables",
    "A list of additional environment variables to set for the game process. Each entry should be in the format 'KEY=VALUE'.",
)


class EnvironmentVariables(FeatureProvider):
    """Feature provider for setting additional, user-defined environment variables.

    This class reads the `ENVIRONMENT_VARIABLES` configuration property (a list of
    'KEY=VALUE' entries) and applies each one to the runtime configuration before
    the game process is launched.
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
        """Parses `ENVIRONMENT_VARIABLES` entries and applies each 'KEY=VALUE'
        pair to the runtime configuration's environment variables."""
        env_vars: list[str] = ENVIRONMENT_VARIABLES.get(configuration, [])
        for var in env_vars:
            key_value = var.split("=", 1)
            if len(key_value) == 2:
                key, value = key_value
                self.logger.info(f"Setting environment variable: {key}={value}")
                runtime_configuration.set_environment_variable(key, value)
        return runtime_configuration

    @override
    def execute_in_pipeline(
        self,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        """Logs the environment variables currently set on the runtime configuration."""
        for k, v in (runtime_configuration.environment_variables or {}).items():
            self.logger.info("Using environment:  %s=%s", k, v)
