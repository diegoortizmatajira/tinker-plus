"""
This module defines a ConfigurationProperty class
"""

from collections.abc import Sequence
import logging
from dataclasses import dataclass
from typing import Any, Callable, cast, get_args, get_origin, overload


from core.configuration_types import AcceptedPropertyTypes, ConfigurationDictionary
from core.runtime_configuration import RuntimeConfiguration


@dataclass
class ListItem[T: AcceptedPropertyTypes]:
    """
    Represents an item in a list with a name and value.
    """

    name: str
    value: T | None


@dataclass
class ConfigurationProperty[T_co: AcceptedPropertyTypes]:
    """
    The ConfigurationProperty class represents a property in a configuration
    with an associated name, description, and an optional default value.
    """

    type_ref: type[T_co]
    name: str
    display_name: str
    description: str
    default: T_co | None = None
    values_provider: (
        Callable[[RuntimeConfiguration, logging.Logger], list[ListItem[T_co]]] | None
    ) = None
    values_cache: list[ListItem[T_co]] | None = None
    generated_environment_variable: str | None = None

    def set(
        self,
        configuration: ConfigurationDictionary,
        value: T_co | None,
    ):
        """
        Sets the value of the configuration property in the given configuration dictionary.

        Args:
            configuration (dict): A dictionary representing the configuration.
            value (ConfigurationValueType): The value to set for the property.
        """
        configuration[self.name] = value

    @overload
    def get(self, configuration: ConfigurationDictionary) -> T_co | None:
        pass

    @overload
    def get(self, configuration: ConfigurationDictionary, default: T_co) -> T_co:
        pass

    def __is_list_type_property(self) -> bool:
        """
        Checks if the property is of list type.

        Returns:
            bool: True if the property is of list type, False otherwise.
        """
        expected_origin = get_origin(self.type_ref)
        return expected_origin is list

    def __advanced_type_check(self, value: object) -> bool:
        """
        Performs an advanced type check on the given value to verify
        if it matches the expected type reference of the property.

        Args:
            value (object): The value to be type-checked.

        Returns:
            bool: True if the value matches the expected type reference, False otherwise.
        """
        expected_args = get_args(self.type_ref)
        if len(expected_args) == 0:
            return isinstance(value, self.type_ref)
        expected_origin = cast(type, get_origin(self.type_ref))
        return isinstance(value, expected_origin)

    def get(
        self,
        configuration: ConfigurationDictionary,
        default: T_co | None = None,
    ) -> T_co | None:
        """
        Retrieves the value of the configuration property.

        Args:
            configuration (dict): A dictionary representing the configuration.

        Returns:
            str | None: The value of the property from the configuration if it exists,
                           otherwise the default value.
        """
        value = configuration.get(self.name, self.default)
        # Validate if value is of type T or None
        if value is None:
            return value or default
        if self.__advanced_type_check(value):
            return cast(T_co, value)
        raise TypeError(
            f"Configuration value is not a {self.type_ref} value: {self.name} = {value} (type: {type(value)})"
        )

    def get_or_fail(self, configuration: ConfigurationDictionary) -> T_co:
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
            + " is required and has no default."
        )

    def get_possible_values(
        self, runtime_configuration: RuntimeConfiguration, logger: logging.Logger
    ) -> list[ListItem[T_co]] | None:
        """
        Retrieves the possible values for the configuration property if a values provider is set.

        Returns:
            list[ListItem] | None: A list of possible values or None if no provider is set.
        """
        if not self.values_cache and self.values_provider:
            return self.values_provider(runtime_configuration, logger)
        return self.values_cache

    # pylint: disable=too-many-return-statements
    def translate_to_environment_variable(
        self,
        configuration: ConfigurationDictionary,
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
        if self.__is_list_type_property():
            value = self.get(configuration)
            if value is None:
                return
            value = [str(item) for item in cast(list[str], value)]
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
        configuration: ConfigurationDictionary,
        properties: Sequence["AnyConfigurationProperty"],
    ) -> ConfigurationDictionary:
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


AnyConfigurationProperty = ConfigurationProperty[Any]  # pyright: ignore[reportExplicitAny]
