"""Module for managing compatibility data folders."""

from core.configuration_types import ConfigurationDictionary
from core.feature_provider import FeatureAction, FeatureProvider
from core.file_operations import delete_folder_tree
from core.runtime_configuration import RuntimeConfiguration


class CompatDataFolders(FeatureProvider):
    """Provides actions for managing compatibility data folders."""

    def __init__(self):
        super().__init__(
            "Compat Data Folder",
            [],
            "Data Management",
            actions=[
                FeatureAction(
                    "compat-folder-delete",
                    "Delete compat data folder",
                    "Deletes the existing compat data folder.",
                    self.delete_compat_folder,
                ),
                FeatureAction(
                    "compat-folder-recreate",
                    "Recreate compat data folder",
                    "Recreates the compat data folder.",
                    self.recreate_compat_folder,
                ),
            ],
        )

    def delete_compat_folder(
        self,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> None:
        """Deletes the compatibility data folder.

        Args:
            _configuration (dict): The configuration dictionary for the operation.
            runtime_configuration (RuntimeConfiguration): The runtime
            configuration for the operation.
        """
        if runtime_configuration.steam_environment_data.steam_compat_data_path:
            delete_folder_tree(
                runtime_configuration.steam_environment_data.steam_compat_data_path,
                self.logger,
                dry_run=runtime_configuration.dry_run,
            )

    def recreate_compat_folder(
        self,
        _configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ) -> None:
        """Recreates the compatibility data folder.

        Args:
            _configuration (dict): The configuration dictionary for the operation.
            runtime_configuration (RuntimeConfiguration): The runtime
            configuration for the operation.
        """
        raise NotImplementedError("Recreate compat data folder is not implemented yet.")
