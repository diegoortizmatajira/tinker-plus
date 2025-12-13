"""Feature provider for Wine configuration."""

from typing import Callable, override
from core import process_runner
from core.configuration_property import ConfigurationProperty, ListItem
from core.configuration_types import ConfigurationDictionary
from core.feature_provider import FeatureAction, FeatureProvider
from core.runtime_configuration import ExecutableCommand, RuntimeConfiguration
from core.wine import get_win_version, get_windows_list_items, set_win_version

WINE_DLLOVERRIDES_PROPERTY = ConfigurationProperty(
    str,
    "WINE_DLLOVERRIDES",
    "Wine DLL Overrides",
    "Specifies custom DLL overrides for Wine. The value should be"
    + " a semicolon-separated list of DLL names and their override"
    + " settings (e.g., 'dll1,native;dll2,builtin').",
    generated_environment_variable="WINEDLLOVERRIDES",
)

WINE_FULLSCREEN_FSR_PROPERTY = ConfigurationProperty(
    bool,
    "WINE_FULLSCREEN_FSR",
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
    values_provider=lambda _runtime_configuration, _logger: [
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
    + " in the Fullscreen FSR Mode setting. The value should be a"
    + " resolution scale factor (e.g., '1.5' for 150% scaling).",
    generated_environment_variable="WINE_FULLSCREEN_FSR_CUSTOM_MODE",
)

WINE_WINDOWS_VERSION_PROPERTY = ConfigurationProperty(
    str,
    "WINE_WINDOWS_VERSION",
    "Wine Windows Version",
    "Specifies the Windows version that Wine should emulate."
    + " Common values include 'win7', 'win10', etc.",
    values_provider=get_windows_list_items,
)


class WineConfig(FeatureProvider):
    """Provides Wine configuration features, including custom DLL overrides."""

    def __init__(self):
        super().__init__(
            "Wine Configuration",
            [
                WINE_WINDOWS_VERSION_PROPERTY,
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
                    self.get_action_runner("winetricks"),
                ),
                FeatureAction(
                    "run-winecfg",
                    "Run Winecfg",
                    "Launch Winecfg to configure Wine settings.",
                    self.get_action_runner("winecfg"),
                ),
                FeatureAction(
                    "run-uninstaller",
                    "Run Wine Uninstaller",
                    "Launch the Wine uninstaller to remove installed Windows applications.",
                    self.get_action_runner("wine", "uninstaller"),
                ),
            ],
        )

    def __run(
        self,
        app: str,
        args: str | None,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        try:
            # Install required Winetricks packages
            succeed = process_runner.run_in_wine_prefix(
                ExecutableCommand(app, args),
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

    def get_action_runner(
        self, command: str, args: str | None = None
    ) -> Callable[[ConfigurationDictionary, RuntimeConfiguration], None]:
        """
        Creates and returns a callable that runs a specified command with optional arguments
        in the Wine runtime environment.

        Args:
            command (str): The Wine command to execute (e.g., 'winetricks', 'winecfg').
            args (str | None): Additional arguments to pass to the command. Defaults to None.

        Returns:
            Callable[[ConfigurationDictionary, RuntimeConfiguration], None]:
            A function that takes a configuration dictionary and runtime configuration
            as parameters and executes the specified Wine command with the given arguments.
        """
        return lambda config, runtime_config: self.__run(
            command, args, config, runtime_config
        )

    @override
    def before_execution(
        self,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        windows_version = WINE_WINDOWS_VERSION_PROPERTY.get(_configuration)
        current_windows_version = get_win_version(runtime_configuration, self.logger)
        if windows_version and windows_version != current_windows_version:
            self.logger.info(
                "Setting Custom Wine Windows version to: %s", windows_version
            )
            set_win_version(windows_version, runtime_configuration, self.logger)
