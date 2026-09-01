"""
Feature: Prefix Selection based on received parameters.
"""

from pathlib import Path
from typing import override
from core import (
    FeatureProvider,
    ProcessRunner,
)
from model import (
    CommandCategory,
    RuntimeConfiguration,
    ConfigurationProperty,
    Command,
    ConfigurationDictionary,
)

PREFIX_CUSTOM_PATH_PROPERTY = ConfigurationProperty(
    str,
    "PREFIX_CUSTOM_PATH",
    "Custom WINE Prefix",
    "Allows selection of a specific prefix.",
)


class PrefixSelection(FeatureProvider):
    """
    Represents a feature provider for prefix selection.

    This class uses the CUSTOM_PREFIX_PROPERTY to allow the selection of a specific
    prefix for runtime configurations. It overrides the apply_configuration method
    to modify the runtime configuration based on the given parameters.
    """

    def __init__(self):
        super().__init__("Prefix selection", [PREFIX_CUSTOM_PATH_PROPERTY], "General")

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        """Applies the custom prefix path if configured, otherwise validates
        that a default prefix path is already set on the runtime configuration."""
        custom_prefix = PREFIX_CUSTOM_PATH_PROPERTY.get(configuration)
        if custom_prefix:
            runtime_configuration.prefix_path = custom_prefix
            self.logger.info(
                "Using custom prefix: %s", runtime_configuration.prefix_path
            )
        else:
            if not runtime_configuration.prefix_path:
                raise RuntimeError(
                    "No default or custom prefix path set in runtime configuration."
                )
            self.logger.info(
                "Using default prefix: %s", runtime_configuration.prefix_path
            )

        return runtime_configuration

    @override
    def execute_in_pipeline(
        self,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        """Runs a no-op command through the compatibility tool to force prefix
        creation if the prefix directory does not already exist."""
        custom_prefix_path = Path(runtime_configuration.prefix_path or ".")
        if not custom_prefix_path.exists():
            self.logger.info("Executing mock command, to force prefix creation.")
            _ = ProcessRunner.run_command_with_compatibility_tool(
                Command.from_string(
                    "/bin/echo", category=CommandCategory.COMPATIBILITY_TOOL
                ),
                runtime_configuration,
                self.logger,
            )
