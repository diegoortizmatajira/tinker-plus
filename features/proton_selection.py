"""
Module for selecting proton version.
"""

import pathlib

from typing import List, override
from core import FeatureProvider, ConfigurationProperty, RuntimeConfiguration, ListItem
from core.configuration_property import BINARY_PROPERTY, LIST_PROPERTY
from core.runtime_configuration import PipelineWrapper


def get_proton_versions_list(configuration: RuntimeConfiguration) -> List[ListItem]:
    """
    Retrieves a list of available proton versions from the specified
    steam compatibility tools path.
    """
    folders = pathlib.Path(configuration.steam_compatibility_tools_path or ".").glob(
        "proton"
    )
    return [ListItem(folder.name, folder.name) for folder in folders if folder.is_dir()]


PROTON_VERSION_PROPERTY = ConfigurationProperty(
    "PROTON_VERSION",
    "Defines which proton version to use.",
    values_provider=get_proton_versions_list,
    type=LIST_PROPERTY,
)
PROTON_LOG_PROPERTY = ConfigurationProperty(
    "PROTON_LOG",
    "Enables proton logging when set to '1'.",
    default=False,
    type=BINARY_PROPERTY,
)


class ProtonSelection(FeatureProvider):
    """
    A feature provider for selecting the proton version.

    This class utilizes the 'USE_PROTON' configuration property to define
    which proton version to use. It extends the FeatureProvider class and ensures
    the property is properly initialized.
    """

    def __init__(self):
        super().__init__([PROTON_VERSION_PROPERTY, PROTON_LOG_PROPERTY])

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
        if PROTON_LOG_PROPERTY.get(configuration) == "1":
            runtime_configuration.set_environment_variable("PROTON_LOG", "1")
            self.logger.info("Proton logging enabled.")
        runtime_configuration.steam_compatibility_tool = (
            PROTON_VERSION_PROPERTY.get_string(configuration)
            or runtime_configuration.steam_compatibility_tool
        )

        runtime_configuration.add_pipeline_wrapper(
            PipelineWrapper(
                wrapper=lambda cmd, runtime_configuration: (
                    f"{runtime_configuration.steam_compatibility_tools_path}/"
                    f"{runtime_configuration.steam_compatibility_tool}/proton waitforexitandrun"
                    f" {cmd}"
                ),
            )
        )
        self.logger.info(
            "Using proton version: %s", runtime_configuration.steam_compatibility_tool
        )
        return runtime_configuration
