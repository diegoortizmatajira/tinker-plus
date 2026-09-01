"""Module for Winetricks package installation feature."""

from typing import override
from core import (
    FeatureProvider,
)
from core import FeatureAction, ProcessRunner
from model import (
    ConfigurationDictionary,
    RuntimeConfiguration,
    Command,
    ConfigurationProperty,
)


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
            actions=[
                FeatureAction(
                    "winetricks-install-packages",
                    "Install Winetricks Packages",
                    "Installs required Winetricks packages into game Prefix",
                    self.install_required_winetricks,
                )
            ],
        )

    def install_required_winetricks(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        """
        Installs the required Winetricks packages based on the provided configuration.

        This method checks the configuration for the Winetricks packages to
        install, logs the process, and executes the installation. If no
        packages are specified, the installation process is skipped. Raises a
        RuntimeError if the installation fails.

        Args:
            configuration (dict): The configuration dictionary containing Winetricks settings.
            runtime_configuration (RuntimeConfiguration): The runtime configuration
            for the installation process.
        """
        winetricks = WINETRICKS_PROPERTY.get(configuration, [])
        if len(winetricks) == 0 or winetricks == [""]:
            self.logger.info("No standalone winetricks packages are requested.")
            winetricks = []
            return
        self.logger.info(
            "Installing Winetricks packages: %s",
            ", ".join(winetricks or []),
        )
        try:
            succeed = ProcessRunner.run_in_wine_prefix(
                Command("winetricks", f"--unattended {' '.join(winetricks)}"),
                runtime_configuration,
                self.logger,
            )
            if succeed:
                self.logger.info("Winetricks packages installed successfully.")
            else:
                self.logger.error("Winetricks packages installation failed.")
                raise RuntimeError("Winetricks installation failed")
        except RuntimeError:
            self.logger.error("Failed to install Winetricks packages")
            raise

    @override
    def before_execution(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        """Installs the configured Winetricks packages automatically, unless
        `WINETRICKS_RUN` is disabled."""
        should_run_winetricks = WINETRICKS_RUN_PROPERTY.get(configuration)
        if not should_run_winetricks:
            self.logger.info(
                "Winetricks installation is not going to run automatically."
            )
            return
        self.install_required_winetricks(configuration, runtime_configuration)
