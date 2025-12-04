"""Feature provider for Wine configuration."""

from typing import Any
from core import process_runner
from core.configuration_property import ConfigurationProperty, ListItem
from core.feature_provider import FeatureAction, FeatureProvider
from core.runtime_configuration import ExecutableCommand, RuntimeConfiguration

WINE_DLLOVERRIDES_PROPERTY = ConfigurationProperty(
    str,
    "WINE_DLLOVERRIDES",
    "Wine DLL Overrides",
    "Specifies custom DLL overrides for Wine. The value should be"
    " a semicolon-separated list of DLL names and their override"
    " settings (e.g., 'dll1,native;dll2,builtin').",
    generated_environment_variable="WINEDLLOVERRIDES",
)

WINE_FULLSCREEN_FSR_PROPERTY = ConfigurationProperty(
    bool,
    "WINE_FULLSCREEN_FSR_MODE",
    "Enable Fullscreen FSR Mode",
    "Enables Fullscreen FSR (FidelityFX Super Resolution) mode in Wine",
    generated_environment_variable="WINE_FULLSCREEN_FSR_MODE",
)

WINE_FULLSCREEN_FSR_MODE = ConfigurationProperty(
    str,
    "WINE_FULLSCREEN_FSR_MODE",
    "Fullscreen FSR Mode",
    "Sets the Fullscreen FSR mode for Wine.",
    generated_environment_variable="WINE_FULLSCREEN_FSR_MODE",
    values_provider=lambda *_: [
        ListItem("ultra", "ultra"),
        ListItem("quality", "quality"),
        ListItem("balanced", "balanced"),
        ListItem("performance", "performance"),
    ],
)

WINE_FULLSCREEN_FSR_CUSTOM_MODE_PROPERTY = ConfigurationProperty(
    str,
    "WINE_FULLSCREEN_FSR_CUSTOM_MODE",
    "Custom Fullscreen FSR Mode",
    "Sets a custom Fullscreen FSR mode for Wine when 'custom' is selected"
    " in the Fullscreen FSR Mode setting. The value should be a"
    " resolution scale factor (e.g., '1.5' for 150% scaling).",
    generated_environment_variable="WINE_FULLSCREEN_FSR_CUSTOM_MODE",
)


class WineConfig(FeatureProvider):
    """Provides Wine configuration features, including custom DLL overrides."""

    def __init__(self):
        super().__init__(
            "Wine Configuration",
            [
                WINE_DLLOVERRIDES_PROPERTY,
                WINE_FULLSCREEN_FSR_PROPERTY,
                WINE_FULLSCREEN_FSR_MODE,
                WINE_FULLSCREEN_FSR_CUSTOM_MODE_PROPERTY,
            ],
            "General",
            actions=[
                FeatureAction(
                    "run-winetrics",
                    "Run Winetricks",
                    "Launch Winetricks to manage Wine prefixes.",
                    self.run_winetricks,
                ),
                FeatureAction(
                    "run-winecfg",
                    "Run Winecfg",
                    "Launch Winecfg to configure Wine settings.",
                    self.run_winecfg,
                ),
            ],
        )

    def __run(
        self,
        app: str,
        _configuration: dict[str, Any],
        runtime_configuration: RuntimeConfiguration,
    ):
        try:
            # Install required Winetricks packages
            succeed = process_runner.run_in_wine_prefix(
                ExecutableCommand(app),
                runtime_configuration,
                self.logger,
            )
            if succeed:
                self.logger.info("%s executed successfully.", app)
            else:
                self.logger.error("%s execution failed.", app)
        except RuntimeError as e:
            self.logger.error("Failed to run %s: %s", app, e)
            raise

    def run_winetricks(
        self,
        configuration: dict[str, Any],
        runtime_configuration: RuntimeConfiguration,
    ):
        """
        Executes the Winetricks application for managing Wine prefixes.

        Args:
            configuration (dict[str, Any]): The current configuration settings.
            runtime_configuration (RuntimeConfiguration): The runtime-specific configuration to use.

        Raises:
            RuntimeError: If the application fails to execute.
        """
        self.__run("winetricks", configuration, runtime_configuration)

    def run_winecfg(
        self,
        configuration: dict[str, Any],
        runtime_configuration: RuntimeConfiguration,
    ):
        """
        Executes the Winecfg application for configuring Wine settings.

        Args:
            configuration (dict[str, Any]): The current configuration settings.
            runtime_configuration (RuntimeConfiguration): The runtime-specific configuration to use.

        Raises:
            RuntimeError: If the application fails to execute.
        """
        self.__run("winecfg", configuration, runtime_configuration)
