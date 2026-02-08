"""
Module for selecting proton version.
"""

import logging
from typing import override

from core import (
    FeatureProvider,
    LogFactory,
    SteamUtil,
)
from model import (
    ConfigurationProperty,
    ListItem,
    CommandCategory,
    CommandWrapper,
    CompatToolInfo,
    RuntimeConfiguration,
    ConfigurationDictionary,
)


def get_proton_versions_list(
    _configuration: RuntimeConfiguration, logger: logging.Logger
) -> list[ListItem[str]]:
    """
    Retrieves a list of available proton versions from the specified
    steam compatibility tools path.
    """
    result = [
        ListItem(item.name, item.name)
        for item in CompatToolInfo.get_cache(logger).values()
    ]
    result.sort(key=lambda x: x.name)
    return result


PROTON_VERSION_PROPERTY = ConfigurationProperty(
    str,
    "PROTON_VERSION",
    "Proton Version to use",
    "Defines which proton version to use.",
    values_provider=get_proton_versions_list,
)
PROTON_LOG_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_LOG",
    "Enable Proton Logs",
    "Enables proton logging when set to 'True'.",
    generated_environment_variable="PROTON_LOG",
)
PROTON_NO_D3D10_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_NO_D3D10",
    "PROTON_NO_D3D10",
    "Disable d3d10.dll and dxgi.dll, for D3D10 games which can fall back to and run"
    + " better with D3D9",
    generated_environment_variable="PROTON_NO_D3D10",
)
PROTON_NO_D3D11_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_NO_D3D11",
    "PROTON_NO_D3D11",
    "Disable d3d11.dll, for D3D11 games which can fall back to and run better with D3D9",
    generated_environment_variable="PROTON_NO_D3D11",
)
PROTON_NO_ESYNC_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_NO_ESYNC",
    "PROTON_NO_ESYNC",
    "Do not use eventfd-based in-process synchronization primitives",
    generated_environment_variable="PROTON_NO_ESYNC",
)
PROTON_NO_FSYNC_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_NO_FSYNC",
    "PROTON_NO_FSYNC",
    "Do not use futex-based in-process synchronization primitives",
    generated_environment_variable="PROTON_NO_FSYNC",
)
PROTON_FORCE_LARGE_ADDRESS_AWARE_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_FORCE_LARGE_ADDRESS_AWARE",
    "PROTON_FORCE_LARGE_ADDRESS_AWARE",
    "Force Wine to enable the LARGE_ADDRESS_AWARE flag",
    generated_environment_variable="PROTON_FORCE_LARGE_ADDRESS_AWARE",
)
PROTON_USE_WINED3D_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_USE_WINED3D",
    "PROTON_USE_WINED3D",
    "Use OpenGL-based WineD3D instead of Vulkan-based DXVK for D3D11, D3D10 and D3D9",
    generated_environment_variable="PROTON_USE_WINED3D",
)
PROTON_DXVK_D3D8_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_DXVK_D3D8",
    "PROTON_DXVK_D3D8",
    "Enable DXVK's D3D8 support",
    generated_environment_variable="PROTON_DXVK_D3D8",
)
PROTON_ENABLE_NVAPI_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_ENABLE_NVAPI",
    "PROTON_ENABLE_NVAPI (Proton 8 or earlier)",
    "Enables Proton support for Nvidia's NVAPI GPU and DLSS (in Proton 8 or earlier)",
    generated_environment_variable="PROTON_ENABLE_NVAPI",
)
PROTON_DISABLE_NVAPI_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_DISABLE_NVAPI",
    "PROTON_DISABLE_NVAPI (Proton 9 or later)",
    "Disable Proton support for Nvidia's NVAPI GPU and DLSS (in Proton 9 or later)",
    generated_environment_variable="PROTON_DISABLE_NVAPI",
)
PROTON_HIDE_NVIDIA_GPU_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_HIDE_NVIDIA_GPU",
    "PROTON_HIDE_NVIDIA_GPU",
    "Proton hide Nvidia GPU",
    generated_environment_variable="PROTON_HIDE_NVIDIA_GPU",
)

PROTON_DLSS_INDICATOR_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_DLSS_INDICATOR",
    "PROTON_DLSS_INDICATOR (Proton 10.26 or later)",
    "Enables an on-screen indicator when DLSS is active in Proton games.",
    generated_environment_variable="PROTON_DLSS_INDICATOR",
)
PROTON_FSR4_INDICATOR_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_FSR4_INDICATOR",
    "PROTON_FSR4_INDICATOR (Proton 10.26 or later)",
    "Enables an on-screen indicator when FSR 4 is active in Proton games.",
    generated_environment_variable="PROTON_FSR4_INDICATOR",
)
PROTON_ENABLE_WAYLAND_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_ENABLE_WAYLAND",
    "PROTON_ENABLE_WAYLAND (Proton 10.1 or later)",
    "Enable Wayland support in Proton",
    generated_environment_variable="PROTON_ENABLE_WAYLAND",
)
PROTON_ENABLE_HDR_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_ENABLE_HDR",
    "PROTON_ENABLE_HDR (Proton 10.1 or later)",
    "Enable HDR support in Proton",
    generated_environment_variable="PROTON_ENABLE_HDR",
)

PROTON_USE_WOW64_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_USE_WOW64",
    "PROTON_USE_WOW64 (32-bit Wine prefix) support",
    "Enable Proton WoW64 (32-bit Wine prefix) support",
    generated_environment_variable="PROTON_USE_WOW64",
)

PROTON_PREFER_SDL_PROPERTY = ConfigurationProperty(
    bool,
    "PROTON_PREFER_SDL",
    "PROTON_PREFER_SDL",
    "Expose SDL video driver along with Hidraw (Can fix input issues in some games)",
    generated_environment_variable="PROTON_PREFER_SDL",
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
            "Options",
            [
                PROTON_VERSION_PROPERTY,
                PROTON_LOG_PROPERTY,
                PROTON_ENABLE_WAYLAND_PROPERTY,
                PROTON_ENABLE_HDR_PROPERTY,
                PROTON_ENABLE_NVAPI_PROPERTY,
                PROTON_DISABLE_NVAPI_PROPERTY,
                PROTON_HIDE_NVIDIA_GPU_PROPERTY,
                PROTON_DLSS_INDICATOR_PROPERTY,
                PROTON_FSR4_INDICATOR_PROPERTY,
                PROTON_NO_D3D10_PROPERTY,
                PROTON_NO_D3D11_PROPERTY,
                PROTON_NO_ESYNC_PROPERTY,
                PROTON_NO_FSYNC_PROPERTY,
                PROTON_USE_WINED3D_PROPERTY,
                PROTON_DXVK_D3D8_PROPERTY,
                PROTON_FORCE_LARGE_ADDRESS_AWARE_PROPERTY,
                PROTON_PREFER_SDL_PROPERTY,
                PROTON_USE_WOW64_PROPERTY,
            ],
            "Proton",
        )

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
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

        custom_proton_version = PROTON_VERSION_PROPERTY.get(configuration)
        if custom_proton_version:
            # Get compatibility tool info from cache to verify it exists
            compat_tool_info = CompatToolInfo.from_cache(
                custom_proton_version, self.logger
            )
            if compat_tool_info:
                self.logger.info(
                    "Setting custom proton version: %s", custom_proton_version
                )
                runtime_configuration.steam_compatibility_tool = compat_tool_info.name
                runtime_configuration.steam_compatibility_tools_path = (
                    compat_tool_info.dir
                )
            else:
                self.logger.error(
                    "Selected proton version '%s' not found in compatibility tools cache.",
                    custom_proton_version,
                )
                raise RuntimeError(
                    f"Selected proton version '{custom_proton_version}' not found."
                )

        if not runtime_configuration.steam_compatibility_tool:
            self.logger.error("No steam compatibility tool (proton) version selected.")
            raise RuntimeError("There is no proton version selected.")

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
        runtime_configuration.wine = SteamUtil.get_wine(
            runtime_configuration, self.logger
        )
        runtime_configuration.add_pipeline_wrapper(
            CommandWrapper(
                wrapper=lambda cmd, runtime_configuration: (
                    f"{runtime_configuration.steam_compatibility_tools_path}/"
                    f"{runtime_configuration.steam_compatibility_tool}/proton"
                    f" run {cmd}"
                ),
                applies_for=[
                    CommandCategory.GAME,
                    CommandCategory.COMPATIBILITY_TOOL,
                    CommandCategory.TRAINER,
                ],
            )
        )
        return runtime_configuration
