from typing import override
from core import FeatureProvider, ConfigurationProperty, RuntimeConfiguration


WINETRICKS_PROPERTY = ConfigurationProperty(
    "WINETRICKS",
    "Specifies a list of winetricks packages to install (comma separated).",
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
        wemod_winetricks = (WINETRICKS_PROPERTY.get(configuration) or "").split(",")
        if wemod_winetricks == [""]:
            self.logger.info("No standalone winetricks packages are required")
            wemod_winetricks = []
            return runtime_configuration
        runtime_configuration.add_winetricks(wemod_winetricks)
        self.logger.info(
            "Required standalone winetricks packages: %s", ",".join(wemod_winetricks)
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

        if runtime_configuration.dry_run:
            self.logger.info(
                "[DRY RUN] Would install Winetricks packages: %s",
                ", ".join(runtime_configuration.winetricks or []),
            )
            return

        self.logger.info(
            "Installing Winetricks packages: %s",
            ", ".join(runtime_configuration.winetricks or []),
        )
