"""
This module defines a ConfigurationProperty class
"""

from dataclasses import dataclass
import logging
from typing import Callable, List, Optional, Type, Union, cast, overload


from core.runtime_configuration import RuntimeConfiguration

# Type alias for the optional value type in the get method
ConfigurationValueType = Union[str, List[str], bool]


@dataclass
class ListItem[T]:
    """
    Represents an item in a list with a name and value.
    """

    name: str
    value: Optional[T]


@dataclass
class ConfigurationProperty[T]:
    """
    The ConfigurationProperty class represents a property in a configuration
    with an associated name, description, and an optional default value.
    """

    type_ref: Type[T]
    name: str
    display_name: str
    description: str
    default: Optional[T] = None
    values_provider: Optional[Callable[[RuntimeConfiguration], List[ListItem[T]]]] = (
        None
    )
    values_cache: Optional[List[ListItem[T]]] = None
    generated_environment_variable: Optional[str] = None

    def set(self, configuration: dict, value: Optional[T]):
        """
        Sets the value of the configuration property in the given configuration dictionary.

        Args:
            configuration (dict): A dictionary representing the configuration.
            value (ConfigurationValueType): The value to set for the property.
        """
        configuration[self.name] = value

    @overload
    def get(self, configuration: dict) -> Optional[T]:
        pass

    @overload
    def get(self, configuration: dict, default: T) -> T:
        pass

    def get(self, configuration: dict, default: Optional[T] = None) -> Optional[T]:
        """
        Retrieves the value of the configuration property.

        Args:
            configuration (dict): A dictionary representing the configuration.

        Returns:
            Optional[str]: The value of the property from the configuration if it exists,
                           otherwise the default value.
        """
        value = configuration.get(self.name, self.default)
        # Validate if value is of type T or None
        if value is None:
            return value or default
        if isinstance(value, self.type_ref):
            return value
        raise TypeError(
            f"Configuration value is not a {T} value: {self.name} = {value}"
        )

    def get_or_fail(self, configuration: dict) -> T:
        """
        Retrieves the value of the configuration property or raises an error if not found.

        Args:
            configuration (dict): A dictionary representing the configuration.
        Returns:
            str: The value of the property from the configuration.
        Raises:
            KeyError: If the property is not found in the configuration and has no default.
        """
        value = self.get(configuration)
        if value is not None:
            return value

        raise KeyError(
            f"Configuration property '{self.name}' ({self.description})"
            " is required and has no default."
        )

    def get_possible_values(
        self, runtime_configuration: RuntimeConfiguration
    ) -> Optional[List[ListItem[T]]]:
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
        if self.type_ref is bool:
            value = self.get(configuration)
            if value is None:
                return

            runtime_configuration.set_environment_variable(
                self.generated_environment_variable, "1" if value else "0"
            )
            logger.info("%s option flag set to %s.", self.name, value)
            return
        if self.type_ref is str:
            value = self.get(configuration)
            if value is None:
                return
            value = str(value)
            # Quote the value if it contains spaces or equal signs
            if " " in value or "=" in value:
                value = f'"{value}"'

            runtime_configuration.set_environment_variable(
                self.generated_environment_variable, value
            )
            logger.info('%s parameter set to "%s".', self.name, value)
            return
        if self.type_ref is list:
            value = self.get(configuration)
            if value is None:
                return
            value = [str(item) for item in cast(list, value)]
            runtime_configuration.set_environment_variable(
                self.generated_environment_variable, ",".join(value)
            )
            logger.info("%s parameter set to %s.", self.name, value)
            return
        value = self.get(configuration)
        if value is None:
            return
        runtime_configuration.set_environment_variable(
            self.generated_environment_variable, str(value)
        )
        logger.info("%s parameter set to %s.", self.name, value)

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
