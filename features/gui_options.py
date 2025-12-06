"""GUI Options Feature Provider"""

from typing import Optional, override
from core.configuration_property import ConfigurationProperty
from core.feature_provider import FeatureProvider
from core.runtime_configuration import RuntimeConfiguration

GUI_SHOW_UI_PROPERTY = ConfigurationProperty(
    bool,
    "GUI_SHOW_UI",
    "Show Graphical User Interface on Startup",
    "If true, shows the GUI on startup",
    True,
)
GUI_AUTORUN_TIMEOUT_PROPERTY = ConfigurationProperty(
    int,
    "GUI_AUTORUN_TIMEOUT",
    "Autorun Timeout (seconds)",
    "Time in seconds before the GUI automatically starts the last launched game. Set to 0 to disable.",
    3,
)


class GuiOptions(FeatureProvider):
    """Provides GUI-related options such as showing the interface on startup
    and configuring the auto-run timeout."""

    def __init__(self):
        super().__init__(
            "GUI Options",
            [
                GUI_SHOW_UI_PROPERTY,
                GUI_AUTORUN_TIMEOUT_PROPERTY,
            ],
            "UI",
        )
        self.use_ui: bool = True
        self.autorun_timeout: int = 3

    @override
    def build_configuration(
        self, sourced_configuration: dict, _runtime_configuration: RuntimeConfiguration
    ) -> dict:
        config = super().build_configuration(
            sourced_configuration, _runtime_configuration
        )
        # Expose configuration values to the instance
        self.use_ui = GUI_SHOW_UI_PROPERTY.get_or_fail(config)
        self.logger.info(
            f"Configuration for displaying the Graphical User Interface is set to: {self.use_ui}"
        )
        self.autorun_timeout = GUI_AUTORUN_TIMEOUT_PROPERTY.get_or_fail(config)
        self.logger.info(
            f"Configuration for GUI autorun timeout is set to: {self.autorun_timeout}"
        )
        return config


CURRENT_GUI_OPTIONS = GuiOptions()
