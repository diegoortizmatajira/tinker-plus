from typing import override
from core import (
    FeatureProvider,
    ConfigurationProperty,
    RuntimeConfiguration,
    process_runner,
)
from core.configuration_property import MULTIVALUELIST_PROPERTY
from core.defaults import WINETRICKS_LOG_FILE


WINETRICKS_PROPERTY = ConfigurationProperty(
    "WINETRICKS",
    "Specifies a list of winetricks packages to install (comma separated).",
    type=MULTIVALUELIST_PROPERTY,
)


class WinetricksInstall(FeatureProvider):
    def __init__(self):
        super().__init__(
            [
                WINETRICKS_PROPERTY,
            ]
        )

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        winetricks = (WINETRICKS_PROPERTY.get(configuration) or "").split(",")
        if winetricks == [""]:
            self.logger.info("No standalone winetricks packages are required")
            winetricks = []
            return runtime_configuration
        runtime_configuration.add_winetricks(winetricks)
        self.logger.info(
            "Required standalone winetricks packages: %s", ",".join(winetricks)
        )

        return runtime_configuration

    @override
    def execute_in_pipeline(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        if (
            not runtime_configuration.winetricks
            or len(runtime_configuration.winetricks) == 0
        ):
            self.logger.info("No Winetricks packages to install.")
            return

        self.logger.info(
            "Installing Winetricks packages: %s",
            ", ".join(runtime_configuration.winetricks or []),
        )
        try:
            process_runner.run_in_wine_prefix(
                f'winetricks --unattended "{" ".join(runtime_configuration.winetricks)}"',
                runtime_configuration,
                self.logger,
                WINETRICKS_LOG_FILE,
            )
        except RuntimeError:
            self.logger.error("Failed to install Winetricks packages")
            raise
