"""
Module for selecting proton version.
"""

import os
import pathlib

from typing import List, override
from core import FeatureProvider, ConfigurationProperty, RuntimeConfiguration, ListItem
from core.log_storage import LogFactory
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


PROTON_LAST_COMPATIBILITY_TOOL_PATH_PROPERTY = ConfigurationProperty(
    str,
    "PROTON_LAST_COMPATIBILITY_TOOL_PATH",
    "The last used steam compatibility tools path.",
)

PROTON_LAST_COMPATIBILITY_TOOL_PROPERTY = ConfigurationProperty(
    str,
    "PROTON_LAST_COMPATIBILITY_TOOL",
    "The last used steam compatibility tool.",
)

PROTON_VERSION_PROPERTY = ConfigurationProperty(
    str,
    "PROTON_VERSION",
    "Defines which proton version to use.",
    values_provider=get_proton_versions_list,
)
PROTON_LOG_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_LOG",
    "Enables proton logging when set to '1'.",
    generated_environment_variable="PROTON_LOG",
)
PROTON_NO_D3D10_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_NO_D3D10",
    "Disable d3d10.dll and dxgi.dll, for D3D10 games which can fall back to and run"
    + " better with D3D9",
    generated_environment_variable="PROTON_NO_D3D10",
)
PROTON_NO_D3D11_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_NO_D3D11",
    "Disable d3d11.dll, for D3D11 games which can fall back to and run better with D3D9",
    generated_environment_variable="PROTON_NO_D3D11",
)
PROTON_NO_ESYNC_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_NO_ESYNC",
    "Do not use eventfd-based in-process synchronization primitives",
    generated_environment_variable="PROTON_NO_ESYNC",
)
PROTON_NO_FSYNC_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_NO_FSYNC",
    "Do not use futex-based in-process synchronization primitives",
    generated_environment_variable="PROTON_NO_FSYNC",
)
PROTON_FORCE_LARGE_ADDRESS_AWARE_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_FORCE_LARGE_ADDRESS_AWARE",
    "Force Wine to enable the LARGE_ADDRESS_AWARE flag",
    generated_environment_variable="PROTON_FORCE_LARGE_ADDRESS_AWARE",
)
PROTON_USE_WINED3D_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_USE_WINED3D",
    "Use OpenGL-based WineD3D instead of Vulkan-based DXVK for D3D11, D3D10 and D3D9",
    generated_environment_variable="PROTON_USE_WINED3D",
)
PROTON_DXVK_D3D8_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_DXVK_D3D8",
    "Enable DXVK's D3D8 support",
    generated_environment_variable="PROTON_DXVK_D3D8",
)
PROTON_DISABLE_NVAPI_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_DISABLE_NVAPI",
    "Disable Proton support for Nvidia's NVAPI GPU and DLSS",
    generated_environment_variable="PROTON_DISABLE_NVAPI",
)
PROTON_HIDE_NVIDIA_GPU_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_HIDE_NVIDIA_GPU",
    "Proton hide Nvidia GPU",
    generated_environment_variable="PROTON_HIDE_NVIDIA_GPU",
)


class ProtonSelection(FeatureProvider):
    """
    A feature provider for selecting the proton version.

    This class utilizes the 'USE_PROTON' configuration property to define
    which proton version to use. It extends the FeatureProvider class and ensures
    the property is properly initialized.
    """

    def __init__(self):
        super().__init__(
            [
                PROTON_VERSION_PROPERTY,
                PROTON_LOG_PROPERTY,
                PROTON_NO_D3D10_PROPERTY,
                PROTON_NO_D3D11_PROPERTY,
                PROTON_NO_ESYNC_PROPERTY,
                PROTON_NO_FSYNC_PROPERTY,
                PROTON_FORCE_LARGE_ADDRESS_AWARE_PROPERTY,
                PROTON_USE_WINED3D_PROPERTY,
                PROTON_DISABLE_NVAPI_PROPERTY,
                PROTON_HIDE_NVIDIA_GPU_PROPERTY,
                PROTON_DXVK_D3D8_PROPERTY,
            ]
        )

    def __get_wine(self, runtime_configuration: RuntimeConfiguration) -> str:
        """
        Retrieves the Wine executable path from the runtime configuration.

        Returns:
            str: The Wine executable path.
        """

        compat_tool_path = os.path.join(
            runtime_configuration.steam_compatibility_tools_path or "missing",
            runtime_configuration.steam_compatibility_tool or "missing",
        )
        proton_wine = os.path.join(compat_tool_path, "dist/bin/wine")
        ge_proton_wine = os.path.join(compat_tool_path, "files/bin/wine")
        self.logger.debug("Checking for Proton Wine at: %s", proton_wine)
        if os.path.isfile(proton_wine):
            self.logger.info("Found Proton Wine at: %s", proton_wine)
            return proton_wine
        self.logger.debug("Checking for GE-Proton Wine at: %s", ge_proton_wine)
        if os.path.isfile(ge_proton_wine):
            self.logger.info("Found GE-Proton Wine at: %s", ge_proton_wine)
            return ge_proton_wine
        self.logger.warning(
            "Could not find a valid Wine executable in the compatibility tool path."
        )
        return ""

    @override
    def build_configuration(
        self, sourced_configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> dict:
        sourced_configuration = super().build_configuration(
            sourced_configuration, runtime_configuration
        )
        if runtime_configuration.steam_compatibility_tools_path:
            PROTON_LAST_COMPATIBILITY_TOOL_PATH_PROPERTY.set(
                sourced_configuration,
                runtime_configuration.steam_compatibility_tools_path,
            )
        if runtime_configuration.steam_compatibility_tool:
            PROTON_LAST_COMPATIBILITY_TOOL_PROPERTY.set(
                sourced_configuration,
                runtime_configuration.steam_compatibility_tool,
            )
        return sourced_configuration

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

        runtime_configuration.steam_compatibility_tool = (
            PROTON_VERSION_PROPERTY.get(configuration)
            or runtime_configuration.steam_compatibility_tool
            or PROTON_LAST_COMPATIBILITY_TOOL_PROPERTY.get(configuration)
        )
        if not runtime_configuration.steam_compatibility_tool:
            self.logger.error("No steam compatibility tool (proton) version selected.")
            raise RuntimeError("There is no proton version selected.")

        if not runtime_configuration.steam_compatibility_tools_path:
            runtime_configuration.steam_compatibility_tools_path = (
                PROTON_LAST_COMPATIBILITY_TOOL_PATH_PROPERTY.get(configuration)
            )
            self.logger.info(
                "Restored last used steam compatibility tools path as "
                "it was not set by runtime provider."
            )
        self.logger.info(
            "Using Steam Compatibility Tool: %s",
            runtime_configuration.steam_compatibility_tool,
        )
        self.logger.info(
            "Using Steam Compatibility Tools path: %s",
            runtime_configuration.steam_compatibility_tools_path,
        )

        proton_logs_enabled = PROTON_LOG_PROPERTY.get(configuration)
        if proton_logs_enabled:
            log_dir = LogFactory.singleton().get_log_folder()
            self.logger.info('Enabling proton logs output to directory: "%s"', log_dir)
            runtime_configuration.set_environment_variable("PROTON_LOG_DIR", log_dir)

        # Get the Wine executable path corresponding to the selected proton version
        runtime_configuration.wine = self.__get_wine(runtime_configuration)
        runtime_configuration.add_pipeline_wrapper(
            PipelineWrapper(
                wrapper=lambda cmd, runtime_configuration: (
                    f"{runtime_configuration.steam_compatibility_tools_path}/"
                    f"{runtime_configuration.steam_compatibility_tool}/proton"
                    f" run {cmd}"
                ),
                is_global_wrapper=False,
                is_fork_wrapper=True,
            )
        )
        return runtime_configuration
