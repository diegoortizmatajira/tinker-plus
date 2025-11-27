"""
Feature: Prefix Selection based on received parameters.
"""

from pathlib import Path
from typing import override
from core import (
    FeatureProvider,
    ConfigurationProperty,
    RuntimeConfiguration,
)
from core.process_runner import run_command_with_compatibility_tool

CUSTOM_PREFIX_PROPERTY = ConfigurationProperty(
    str, "CUSTOM_PREFIX", "Allows selection of a specific prefix."
)


class PrefixSelection(FeatureProvider):
    """
    Represents a feature provider for prefix selection.

    This class uses the CUSTOM_PREFIX_PROPERTY to allow the selection of a specific
    prefix for runtime configurations. It overrides the apply_configuration method
    to modify the runtime configuration based on the given parameters.
    """

    def __init__(self):
        super().__init__([CUSTOM_PREFIX_PROPERTY])

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        custom_prefix = CUSTOM_PREFIX_PROPERTY.get(configuration)
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
        self, _configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        custom_prefix_path = Path(runtime_configuration.prefix_path or ".")
        if not custom_prefix_path.exists():
            self.logger.info("Executing mock command, to force prefix creation.")
            run_command_with_compatibility_tool(
                "/bin/echo", runtime_configuration, self.logger
            )
