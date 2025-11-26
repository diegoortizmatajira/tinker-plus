"""
This module defines a ConfigurationProperty class
"""

from dataclasses import dataclass
import logging
from typing import Callable, List, Literal, Optional, Union, overload


from core.runtime_configuration import RuntimeConfiguration

# Type alias for the optional value type in the get method
ConfigurationValueType = Union[str, List[str], bool]


@dataclass
class ListItem:
    """
    Represents an item in a list with a name and value.
    """

    name: str
    value: Optional[ConfigurationValueType]


BINARY_PROPERTY = "BINARY_PROPERTY"
LIST_PROPERTY = "LIST_PROPERTY"
MULTIVALUELIST_PROPERTY = "MULTIVALUELIST_PROPERTY"
TEXT_PROPERTY = "TEXT_PROPERTY"


@dataclass
class ConfigurationProperty:
    """
    The ConfigurationProperty class represents a property in a configuration
    with an associated name, description, and an optional default value.
    """

    name: str
    description: str
    default: Optional[ConfigurationValueType] = None
    values_provider: Optional[Callable[[RuntimeConfiguration], List[ListItem]]] = None
    values_cache: Optional[List[ListItem]] = None
    type: Literal[
        "BINARY_PROPERTY", "LIST_PROPERTY", "MULTIVALUELIST_PROPERTY", "TEXT_PROPERTY"
    ] = TEXT_PROPERTY
    generated_environment_variable: Optional[str] = None

    def set(self, configuration: dict, value: Optional[ConfigurationValueType]):
        """
        Sets the value of the configuration property in the given configuration dictionary.

        Args:
            configuration (dict): A dictionary representing the configuration.
            value (ConfigurationValueType): The value to set for the property.
        """
        configuration[self.name] = value

    @overload
    def get(self, configuration: dict) -> Optional[ConfigurationValueType]:
        pass

    @overload
    def get(
        self, configuration: dict, default: ConfigurationValueType
    ) -> ConfigurationValueType:
        pass

    def get(
        self, configuration: dict, default: Optional[ConfigurationValueType] = None
    ) -> Optional[ConfigurationValueType]:
        """
        Retrieves the value of the configuration property.

        Args:
            configuration (dict): A dictionary representing the configuration.

        Returns:
            Optional[str]: The value of the property from the configuration if it exists,
                           otherwise the default value.
        """
        return configuration.get(self.name, self.default) or default

    @overload
    def get_boolean(self, configuration: dict) -> Optional[bool]:
        """
        Retrieves the value of the configuration property as a boolean.

        Args:
            configuration (dict): A dictionary representing the configuration.

        Returns:
            Optional[bool]: The value of the property as a boolean if it exists,
                            otherwise the default value.

        Raises:
            TypeError: If the configuration value is not a boolean.
        """

    @overload
    def get_boolean(self, configuration: dict, default: bool) -> bool:
        """
        Retrieves the value of the configuration property as a boolean, or
        returns the specified default if the property is not found.

        Args:
            configuration (dict): A dictionary representing the configuration.
            default (bool): The default value to return if the property is not found.

        Returns:
            bool: The value of the property as a boolean, or the specified default value.
        """

    def get_boolean(
        self, configuration: dict, default: Optional[bool] = None
    ) -> Optional[bool]:
        """
        Retrieves the value of the configuration property as a boolean.

        Args:
            configuration (dict): A dictionary representing the configuration.

        Returns:
            Optional[bool]: The value of the property as a boolean if it exists,
                            otherwise the default value.

        Raises:
            TypeError: If the configuration value is not a boolean.
        """
        value = self.get(configuration)
        if value is None or isinstance(value, bool):
            return value or default
        raise TypeError(
            f"Configuration value is not a boolean value: {self.name} = {value}"
        )

    @overload
    def get_string(self, configuration: dict, default: str) -> str:
        """
        Retrieves the value of the configuration property as a string, or
        returns the specified default if the property is not found.

        Args:
            configuration (dict): A dictionary representing the configuration.
            default (str): The default value to return if the property is not found.

        Returns:
            str: The value of the property as a string if it exists,
                 otherwise the specified default value.

        Raises:
            TypeError: If the configuration value is not a string.
        """

    @overload
    def get_string(self, configuration: dict) -> Optional[str]:
        """
        Retrieves the value of the configuration property as a string.

        Args:
            configuration (dict): A dictionary representing the configuration.

        Returns:
            Optional[str]: The value of the property as a string if it exists,
                           otherwise the default value.

        Raises:
            TypeError: If the configuration value is not a string.
        """

    def get_string(
        self, configuration: dict, default: Optional[str] = None
    ) -> Optional[str]:
        """
        Retrieves the value of the configuration property as a string.

        Args:
            configuration (dict): A dictionary representing the configuration.

        Returns:
            Optional[str]: The value of the property as a string if it exists,
                           otherwise the default value.

        Raises:
            TypeError: If the configuration value is not a string.
        """
        value = self.get(configuration)
        if value is None or isinstance(value, str):
            return value or default
        raise TypeError(f"Configuration value is not a string: {self.name} = {value}")

    @overload
    def get_string_list(self, configuration: dict) -> Optional[List[str]]:
        pass

    @overload
    def get_string_list(self, configuration: dict, default: List[str]) -> List[str]:
        pass

    def get_string_list(
        self, configuration: dict, default: Optional[List[str]] = None
    ) -> Optional[List[str]]:
        """
        Retrieves the value of the configuration property as a list of strings.

        Args:
            configuration (dict): A dictionary representing the configuration.

        Returns:
            Optional[List[str]]: The value of the property as a list of strings
                                 if it exists, otherwise None.

        Raises:
            TypeError: If the configuration value is not a list of strings.
        """
        value = self.get(configuration)
        if value is None or isinstance(value, list):
            return value or default
        raise TypeError(
            f"Configuration value is not a string list: {self.name} = {value}"
        )

    def get_or_fail(self, configuration: dict) -> ConfigurationValueType:
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

    # pylint: disable=too-many-return-statements
    def translate_to_environment_variable(
        self,
        configuration: dict,
        runtime_configuration: RuntimeConfiguration,
        logger: logging.Logger,
    ):
        """
        Translates the configuration property to an environment variable in the
        runtime configuration.

        Args:
            configuration (dict): A dictionary representing the configuration.
            runtime_configuration (RuntimeConfiguration): The runtime configuration object.
        """
        if not self.generated_environment_variable:
            return
        if self.type == BINARY_PROPERTY:
            value = self.get_boolean(configuration)
            if value is None:
                return

            runtime_configuration.set_environment_variable(
                self.generated_environment_variable, "1" if value else "0"
            )
            logger.info("%s option flag set to %s.", self.name, value)
            return
        if self.type in (TEXT_PROPERTY, LIST_PROPERTY):
            value = self.get_string(configuration)
            if value is None:
                return
            # Quote the value if it contains spaces or equal signs
            if " " in value or "=" in value:
                value = f'"{value}"'

            runtime_configuration.set_environment_variable(
                self.generated_environment_variable, value
            )
            logger.info('%s parameter set to "%s".', self.name, value)
            return
        if self.type == MULTIVALUELIST_PROPERTY:
            value = self.get_string_list(configuration)
            if value is None:
                return

            runtime_configuration.set_environment_variable(
                self.generated_environment_variable, ",".join(value)
            )
            logger.info("%s parameter set to %s.", self.name, value)
            return

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
