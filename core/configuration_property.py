"""
This module defines a ConfigurationProperty class
"""

from dataclasses import dataclass
from typing import Callable, List, Literal, Optional

from core.runtime_configuration import RuntimeConfiguration


@dataclass
class ListItem:
    """
    Represents an item in a list with a name and value.
    """

    name: str
    value: str


BINARY_PROPERTY = "BINARY_PROPERTY"
LIST_PROPERTY = "LIST_PROPERTY"
TEXT_PROPERTY = "TEXT_PROPERTY"


@dataclass
class ConfigurationProperty:
    """
    The ConfigurationProperty class represents a property in a configuration
    with an associated name, description, and an optional default value.
    """

    name: str
    description: str
    default: Optional[str] = None
    values_provider: Optional[Callable[[RuntimeConfiguration], List[ListItem]]] = None
    values_cache: Optional[List[ListItem]] = None
    type: Literal["BINARY_PROPERTY", "LIST_PROPERTY", "TEXT_PROPERTY"] = TEXT_PROPERTY

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

    def get_possible_values(
        self, runtime_configuration: RuntimeConfiguration
    ) -> Optional[List[ListItem]]:
        """
        Retrieves the possible values for the configuration property if a values provider is set.

        Returns:
            Optional[List[ListItem]]: A list of possible values or None if no provider is set.
        """
        if not self.values_cache and self.values_provider:
            return self.values_provider(runtime_configuration)
        return self.values_cache

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
            if prop.name not in configuration:
                configuration[prop.name] = prop.default
        return configuration
