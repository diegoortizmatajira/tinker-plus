"""
This module defines a ConfigurationProperty class
"""

from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass
class ConfigurationProperty:
    """
    The ConfigurationProperty class represents a property in a configuration
    with an associated name, description, and an optional default value.
    """

    name: str
    description: str
    default: Optional[str] = None
    values_provider: Optional[Callable[[], List[str]]] = None

    def get(self, configuration: dict) -> Optional[str]:
        """
        Retrieves the value of the configuration property.

        Args:
            configuration (dict): A dictionary representing the configuration.

        Returns:
            Optional[str]: The value of the property from the configuration if it exists,
                           otherwise the default value.
        """
        if self.name in configuration:
            return configuration[self.name]
        return self.default

    def get_or_fail(self, configuration: dict) -> str:
        """
        Retrieves the value of the configuration property or raises an error if not found.

        Args:
            configuration (dict): A dictionary representing the configuration.
        Returns:
            str: The value of the property from the configuration.
        Raises:
            KeyError: If the property is not found in the configuration and has no default.
        """
        if self.name in configuration:
            return configuration[self.name]
        if self.default is not None:
            return self.default
        raise KeyError(
            f"Configuration property '{self.name}' ({self.description})"
            " is required and has no default."
        )

    def get_possible_values(self) -> Optional[List[str]]:
        """
        Retrieves the possible values for the configuration property if a values provider is set.

        Returns:
            Optional[List[str]]: A list of possible values or None if no provider is set.
        """
        if self.values_provider:
            return self.values_provider()
        return None

    @staticmethod
    def initialize_defaults(
        configuration: dict, properties: list["ConfigurationProperty"]
    ) -> dict:
        """
        Initializes the configuration dictionary with default values for properties
        that are not already present.

        Args:
            configuration (dict): A dictionary representing the configuration.
            properties (list[ConfigurationProperty]): A list of ConfigurationProperty instances.
        Returns:
            dict: The updated configuration dictionary with default values set.
        """
        for prop in properties:
            if prop.name not in configuration and prop.default is not None:
                configuration[prop.name] = prop.default
        return configuration
