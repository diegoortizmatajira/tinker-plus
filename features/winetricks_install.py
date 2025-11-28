"""Module for Winetricks package installation feature."""

from typing import override
from core import (
    FeatureProvider,
    ConfigurationProperty,
    RuntimeConfiguration,
    process_runner,
)
from core.defaults import WINETRICKS_LOG_FILE


WINETRICKS_RUN_PROPERTY = ConfigurationProperty(
    bool,
    "WINETRICKS_RUN",
    "Execute Winetricks in pipeline",
    "Specifies if winetricks should be run (true/false).",
    default=True,
)

WINETRICKS_PROPERTY = ConfigurationProperty(
    list,
    "WINETRICKS",
    "Winetricks Packages",
    "Specifies a list of winetricks packages to install (comma separated).",
    default=[],
)


class WinetricksInstall(FeatureProvider):
    """Feature to install standalone Winetricks packages."""

    def __init__(self):
        super().__init__(
            "Winetricks Install",
            [
                WINETRICKS_RUN_PROPERTY,
                WINETRICKS_PROPERTY,
            ],
            "Pipeline",
        )

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        should_run_winetricks = WINETRICKS_RUN_PROPERTY.get(configuration)
        runtime_configuration.install_winetricks = (
            True if should_run_winetricks is None else should_run_winetricks
        )
        if runtime_configuration.install_winetricks:
            self.logger.info("Winetricks installation will run automatically.")
        else:
            self.logger.info(
                "Winetricks installation is not going to run automatically."
            )
        winetricks = WINETRICKS_PROPERTY.get(configuration, [])
        if len(winetricks) == 0 or winetricks == [""]:
            self.logger.info("No standalone winetricks packages are requested.")
            winetricks = []
            return runtime_configuration
        runtime_configuration.add_winetricks(winetricks)
        self.logger.info(
            "Requested standalone winetricks packages: %s", ",".join(winetricks)
        )

        return runtime_configuration

    @override
    def execute_in_pipeline(
        self, _configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        if not runtime_configuration.install_winetricks:
            self.logger.info("Winetricks installation is not running automatically.")
            return
        if (
            not runtime_configuration.winetricks
            or len(runtime_configuration.winetricks) == 0
        ):
            self.logger.info("No Winetricks packages required to be installed.")
            return

        self.logger.info(
            "Installing Winetricks packages: %s",
            ", ".join(runtime_configuration.winetricks or []),
        )
        try:
            succeed = process_runner.run_in_wine_prefix(
                f"winetricks --unattended {' '.join(runtime_configuration.winetricks)}",
                runtime_configuration,
                self.logger,
                WINETRICKS_LOG_FILE,
            )
            if succeed:
                self.logger.info("Winetricks packages installed successfully.")
            else:
                self.logger.error("Winetricks packages installation failed.")
                raise RuntimeError("Winetricks installation failed")
        except RuntimeError:
            self.logger.error("Failed to install Winetricks packages")
            raise
