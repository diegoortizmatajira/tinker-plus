"""
Feature Provider Base Class
"""

import logging
from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable

from model import RuntimeConfiguration, ConfigurationDictionary

from .configuration_property import (
    AnyConfigurationProperty,
    ConfigurationProperty,
)
from .log_storage import LogFactory


@dataclass
class FeatureAction:
    """
    Represents an action that can be performed as part of a feature.

    Attributes:
        alias (str): A shorthand or alias name for the action.
        name (str): The formal name of the action.
        description (str): A brief description of what the action does.
        action (Callable): A callable that executes the action, taking a dictionary
            of parameters and a runtime configuration as arguments.
    """

    alias: str
    name: str
    description: str
    action: Callable[[ConfigurationDictionary, RuntimeConfiguration], None]


class FeatureProvider(ABC):
    """
    Base class for feature providers in the system.

    This class provides the blueprint for creating feature providers, including
    handling default property configurations and applying configurations to a runtime setup.
    """

    def __init__(
        self,
        name: str,
        properties: Sequence[AnyConfigurationProperty],
        category: str = "General",
        actions: Sequence[FeatureAction] | None = None,
    ):
        self.properties: Sequence[AnyConfigurationProperty] = properties
        self.name: str = name
        self.category: str = category
        self.actions: Sequence[FeatureAction] = actions or []
        self.logger: logging.Logger = LogFactory.singleton().get_logger(
            self.__class__.__name__
        )

    def build_configuration(
        self,
        sourced_configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ) -> ConfigurationDictionary:
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

    def override_configuration(
        self,
        sourced_configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ) -> ConfigurationDictionary:
        """
        Hook method to override configuration settings after reading from sources and before
        applying.

        Args:
            sourced_configuration (dict): The initial configuration dictionary to be sourced.

        Returns:
            dict: The updated configuration dictionary with overrides applied.
        """
        return sourced_configuration

    def apply_configuration(
        self,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        """
        Abstract method to apply configuration settings to the runtime configuration.

        Args:
            configuration (dict): The configuration settings to be applied.
            runtime_configuration (RuntimeConfiguration): The runtime configuration
            to which the settings are applied.

        Returns:
            RuntimeConfiguration: The updated runtime configuration with the applied settings.
        """
        return runtime_configuration

    def before_execution(
        self,
        _configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ):
        """
        Hook method called before the execution of game pipeline.
        """

    def after_execution(
        self,
        _configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ):
        """
        Hook method called after the execution of game pipeline.
        """

    def execute_in_pipeline(
        self,
        _configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ):
        """
        Abstract method to execute the feature provider in the runtime pipeline.

        Args:
            configuration (dict): The configuration settings to be used during execution.
            runtime_configuration (RuntimeConfiguration): The runtime environment
            used during the pipeline execution.
        """

    def try_apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        """
        Attempts to apply the configuration settings to the runtime configuration,
        handling any exceptions that may arise during the process.

        Args:
            configuration (dict): The configuration settings to be applied.
            runtime_configuration (RuntimeConfiguration): The runtime configuration
            to which the settings are applied.

        Returns:
            RuntimeConfiguration: The updated runtime configuration with the applied settings.

        Raises:
            RuntimeError: If an error occurs while applying the configuration.
        """
        try:
            # Translate properties to environment variables, if the property defines one
            for prop in self.properties:
                prop.translate_to_environment_variable(
                    configuration, runtime_configuration, self.logger
                )
            return self.apply_configuration(configuration, runtime_configuration)
        except KeyError as e:
            self.logger.error("Missing configuration key: %s", e)
            raise RuntimeError(
                f"Configuration key missing in {self.__class__.__name__}"
            ) from e
        except Exception as e:
            self.logger.error(
                "Error applying configuration: %s",
                e,
            )
            raise RuntimeError(
                f"Failed to apply configuration in {self.__class__.__name__}"
            ) from e

    def try_execute_in_pipeline(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        """
        Attempts to execute the feature provider in the runtime pipeline,
        handling any exceptions that may arise during the process.

        Args:
            configuration (dict): The configuration settings to be used during execution.
            runtime_configuration (RuntimeConfiguration): The runtime environment
            used during the pipeline execution.

        Raises:
            RuntimeError: If an error occurs during pipeline execution.
        """
        try:
            self.execute_in_pipeline(configuration, runtime_configuration)
        except Exception as e:
            self.logger.error(
                "Error executing in pipeline: %s",
                e,
            )
            raise RuntimeError(
                f"Failed to execute in pipeline in {self.__class__.__name__}"
            ) from e

    def validate(
        self,
        _configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ) -> Sequence[str]:
        """
        Validates the current configuration and runtime setup.

        Args:
            _configuration (ConfigurationDictionary): The configuration settings to validate.
            _runtime_configuration (RuntimeConfiguration): The runtime
            environment to validate against.

        Returns:
            Sequence[str]: A list of validation error messages, or an empty
            list if no issues are found.
        """
        return []
