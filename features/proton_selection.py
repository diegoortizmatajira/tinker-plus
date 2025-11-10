"""
Module for selecting proton version.
"""

from typing import override
from core import FeatureProvider, ConfigurationProperty, RuntimeConfiguration

PROTON_VERSION_PROPERTY = ConfigurationProperty(
    "USE_PROTON", "Defines which proton version to use."
)


class ProtonSelection(FeatureProvider):
    """
    A feature provider for selecting the proton version.

    This class utilizes the 'USE_PROTON' configuration property to define
    which proton version to use. It extends the FeatureProvider class and ensures
    the property is properly initialized.
    """

    def __init__(self):
        super().__init__([PROTON_VERSION_PROPERTY])

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        """
        Applies the given configuration to the runtime configuration.

        This method sets the 'use_proton' attribute in the runtime configuration
        based on the 'USE_PROTON' value provided in the configuration dictionary.
        If 'USE_PROTON' is not specified, an empty string is assigned.

        Args:
            configuration (dict): The configuration dictionary containing keys
                and values for runtime adjustments.
            runtime_configuration (RuntimeConfiguration): The runtime configuration
                object to apply the settings.

        Returns:
            RuntimeConfiguration: The updated runtime configuration object.
        """
        runtime_configuration.use_proton = PROTON_VERSION_PROPERTY.get_or_fail(
            configuration
        )
        return runtime_configuration
