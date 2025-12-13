"""GUI Options Feature Provider"""

from typing import override
from core.configuration_property import ConfigurationProperty
from core.configuration_types import ConfigurationDictionary
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
    (
        "Time in seconds before the GUI automatically starts the last "
        "launched game. Set to 0 to disable."
    ),
    3,
)

GUI_CLOSE_AFTER_RUNNING_GAME_PROPERTY = ConfigurationProperty(
    bool,
    "GUI_CLOSE_AFTER_RUNNING_GAME",
    "Close GUI After Running Game",
    "If true, closes the GUI after launching a game",
    True,
)


class GuiOptions(FeatureProvider):
    """Provides GUI-related options such as showing the interface on startup
    and configuring the auto-run timeout."""

    def __init__(self):
        super().__init__(
            "GUI Options",
            [
                GUI_SHOW_UI_PROPERTY,
                GUI_CLOSE_AFTER_RUNNING_GAME_PROPERTY,
                GUI_AUTORUN_TIMEOUT_PROPERTY,
            ],
            "UI",
        )
        self.use_ui: bool = True
        self.autorun_timeout: int = 3
        self.close_after_running_game: bool = True

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        self.use_ui = GUI_SHOW_UI_PROPERTY.get_or_fail(configuration)
        self.close_after_running_game = (
            GUI_CLOSE_AFTER_RUNNING_GAME_PROPERTY.get_or_fail(configuration)
        )
        self.logger.info(
            f"Configuration for displaying the Graphical User Interface is set to: {self.use_ui}"
        )
        self.autorun_timeout = GUI_AUTORUN_TIMEOUT_PROPERTY.get_or_fail(configuration)
        self.logger.info(
            f"Configuration for GUI autorun timeout is set to: {self.autorun_timeout}"
        )
        return runtime_configuration


CURRENT_GUI_OPTIONS = GuiOptions()
