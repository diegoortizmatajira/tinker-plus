"""
Unit tests for the ProtonSelection class.
"""

import unittest
from unittest.mock import MagicMock, patch

from core.runtime_configuration import RuntimeConfiguration
from features.proton_selection import ProtonSelection, get_proton_versions_list


class TestProtonSelection(unittest.TestCase):
    """Unit tests for the ProtonSelection feature provider."""

    def setUp(self):
        """Prepare the test environment by initializing ProtonSelection."""

        # Initialize runtime configuration mock
        self.mock_runtime_config = MagicMock(spec=RuntimeConfiguration)

        self.proton_selection = ProtonSelection()

    def test_apply_configuration_with_valid_value(self):
        """
        Test that apply_configuration correctly sets the USE_PROTON value
        when provided with a valid value.
        """
        # Mock input configuration and runtime configuration
        configuration = {"USE_PROTON": "PROTON7-21"}
        runtime_configuration = MagicMock(spec=RuntimeConfiguration)

        # Apply configuration
        updated_runtime_config = self.proton_selection.apply_configuration(
            configuration, runtime_configuration
        )

        # Verify the USE_PROTON value was applied
        self.assertEqual(updated_runtime_config.use_proton, "PROTON7-21")

    def test_apply_configuration_with_missing_value(self):
        """
        Test that a KeyError is raised when the USE_PROTON value is missing
        from the configuration dictionary.
        """
        # Mock input configuration and runtime configuration
        configuration = {}  # USE_PROTON not included
        runtime_configuration = MagicMock(spec=RuntimeConfiguration)
        # Set a default value for steam_compatibility_tool to avoid AttributeError
        runtime_configuration.steam_compatibility_tool = "DEFAULT_PROTON"

        # Apply configuration
        self.proton_selection.apply_configuration(configuration, runtime_configuration)
        # Verify the USE_PROTON is set to the default steam_compatibility_tool
        self.assertEqual(runtime_configuration.use_proton, "DEFAULT_PROTON")

    def test_apply_configuration_with_empty_string(self):
        """
        Test that apply_configuration sets the USE_PROTON value to an empty
        string when provided empty input.
        """
        # Mock input configuration and runtime configuration
        configuration = {"USE_PROTON": ""}
        runtime_configuration = MagicMock(spec=RuntimeConfiguration)
        # Set a default value for steam_compatibility_tool to avoid AttributeError
        runtime_configuration.steam_compatibility_tool = "DEFAULT_PROTON"

        # Apply configuration
        updated_runtime_config = self.proton_selection.apply_configuration(
            configuration, runtime_configuration
        )

        # Verify the USE_PROTON is set to an empty string
        self.assertEqual(updated_runtime_config.use_proton, "DEFAULT_PROTON")

    @patch("pathlib.Path")
    def test_get_proton_versions_list(self, mock_pathlib):
        """
        Test that get_proton_versions_list correctly retrieves a list of proton
        versions from the mock runtime configuration.

        Args:
            mock_pathlib: Mocked pathlib.Path object used to simulate file system operations.
        """
        # Arrange
        self.mock_runtime_config.steam_compatibility_tools_path = "/mock/path"
        mock_folder_1 = MagicMock()
        mock_folder_1.is_dir.return_value = True
        mock_folder_1.name = "proton-1"
        mock_folder_2 = MagicMock()
        mock_folder_2.is_dir.return_value = True
        mock_folder_2.name = "proton-2"
        mock_pathlib.return_value.glob.return_value = [mock_folder_1, mock_folder_2]

        # Act
        result = get_proton_versions_list(self.mock_runtime_config)

        # Assert
        self.assertEqual(result, ["proton-1", "proton-2"])
        mock_pathlib.assert_called_with("/mock/path")


if __name__ == "__main__":
    unittest.main()
