"""
Feature Provider Base Class
"""

from abc import ABC, abstractmethod
from typing import List

from .runtime_configuration import RuntimeConfiguration

from .configuration_property import ConfigurationProperty


class FeatureProvider(ABC):
    """
    Base class for feature providers in the system.

    This class provides the blueprint for creating feature providers, including
    handling default property configurations and applying configurations to a runtime setup.
    """

    def __init__(self, properties: List[ConfigurationProperty]):
        self.properties = properties

    def build_configuration(self, sourced_configuration: dict) -> dict:
        """
        Builds and returns the updated configuration dictionary with default
        values initialized based on the property definitions.

        Args:
            sourced_configuration (dict): The initial configuration dictionary to be sourced.

        Returns:
            dict: The updated configuration dictionary with defaults applied.
        """
        sourced_configuration = ConfigurationProperty.initialize_defaults(
            sourced_configuration, self.properties
        )
        return sourced_configuration

    @abstractmethod
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        """
        Abstract method to apply configuration settings to the runtime configuration.

        Args:
            configuration (dict): The configuration settings to be applied.
            runtime_configuration (RuntimeConfiguration): The runtime configuration to which the settings are applied.

        Returns:
            RuntimeConfiguration: The updated runtime configuration with the applied settings.
        """
