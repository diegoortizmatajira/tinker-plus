"""
Feature Provider Base Class
"""

import logging

from abc import ABC, abstractmethod
from typing import List
from .runtime_configuration import RuntimeConfiguration
from .configuration_property import ConfigurationProperty
from .log_storage import logger_factory


class FeatureProvider(ABC):
    """
    Base class for feature providers in the system.

    This class provides the blueprint for creating feature providers, including
    handling default property configurations and applying configurations to a runtime setup.
    """

    def __init__(self, properties: List[ConfigurationProperty]):
        self.properties = properties
        self.logger = logger_factory.get_logger(self.__class__.__name__)

    def build_configuration(
        self, sourced_configuration: dict, game_id: str, app_id: str
    ) -> dict:
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

    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
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

    def execute_in_pipeline(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        """
        Abstract method to execute the feature provider in the runtime pipeline.

        Args:
            configuration (dict): The configuration settings to be used during execution.
            runtime_configuration (RuntimeConfiguration): The runtime environment
            used during the pipeline execution.
        """

    def try_apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
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
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
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
