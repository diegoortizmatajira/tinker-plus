"""
Feature to link user folders to specified locations to manage saved games and settings.
"""

from typing import override
from core import ConfigurationProperty, FeatureProvider, RuntimeConfiguration
from core.config_storage import ConfigStorage

LINK_STEAM_USER_FOLDER_PROPERTY = ConfigurationProperty(
    "LINK_STEAM_USER_FOLDER",
    "If provided links the steam user folder to the given location",
    None,
)

LINK_PUBLIC_USER_FOLDER_PROPERTY = ConfigurationProperty(
    "LINK_PUBLIC_USER_FOLDER",
    "If provided links the public user folder to the given location",
    None,
)


class LinkUserFolders(FeatureProvider):
    """
    A feature to manage user folder links for saved games and settings.

    This class provides functionality to link specific user folders, such as the Steam
    user folder and the public user folder, to specified locations for better
    organization and management.
    """

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(
            [
                LINK_STEAM_USER_FOLDER_PROPERTY,
                LINK_PUBLIC_USER_FOLDER_PROPERTY,
            ]
        )
        self.config_storage = config_storage

    @override
    def execute_in_pipeline(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        # Link Steam user folder if specified
        pass
