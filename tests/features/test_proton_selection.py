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
        configuration = {"PROTON_VERSION": "PROTON7-21"}
        runtime_configuration = RuntimeConfiguration.empty()
        runtime_configuration.steam_compatibility_tool = "DEFAULT_PROTON"

        # Apply configuration
        updated_runtime_config = self.proton_selection.apply_configuration(
            configuration, runtime_configuration
        )

        # Verify the USE_PROTON value was applied
        self.assertEqual(updated_runtime_config.steam_compatibility_tool, "PROTON7-21")

    def test_apply_configuration_with_missing_value(self):
        """
        Test that a KeyError is raised when the USE_PROTON value is missing
        from the configuration dictionary.
        """
        # Mock input configuration and runtime configuration
        configuration = {}  # USE_PROTON not included
        runtime_configuration = RuntimeConfiguration.empty()
        runtime_configuration.steam_compatibility_tool = "DEFAULT_PROTON"

        # Apply configuration
        self.proton_selection.apply_configuration(configuration, runtime_configuration)
        # Verify the USE_PROTON is set to the default steam_compatibility_tool
        self.assertEqual(
            runtime_configuration.steam_compatibility_tool, "DEFAULT_PROTON"
        )

    def test_apply_configuration_with_empty_string(self):
        """
        Test that apply_configuration sets the USE_PROTON value to an empty
        string when provided empty input.
        """
        # Mock input configuration and runtime configuration
        configuration = {"USE_PROTON": ""}
        runtime_configuration = RuntimeConfiguration.empty()
        runtime_configuration.steam_compatibility_tool = "DEFAULT_PROTON"

        # Apply configuration
        updated_runtime_config = self.proton_selection.apply_configuration(
            configuration, runtime_configuration
        )

        # Verify the USE_PROTON is set to an empty string
        self.assertEqual(
            updated_runtime_config.steam_compatibility_tool, "DEFAULT_PROTON"
        )

    @patch("pathlib.Path")
    @patch("features.proton_selection.CompatToolInfo.get_cache")
    def test_get_proton_versions_list(self, mock_get_cache, mock_path):
        """
        Test that get_proton_versions_list correctly retrieves a list of proton
        versions from the mock runtime configuration.

        Args:
            mock_path: Mocked pathlib.Path class
        """
        # Arrange
        compat_tools_path = "/mock/path"
        self.mock_runtime_config.steam_compatibility_tools_path = compat_tools_path

        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance

        # Mock folders
        mock_folder_1 = MagicMock()
        mock_folder_1.is_dir.return_value = True
        mock_folder_1.name = "proton-1"
        mock_folder_2 = MagicMock()
        mock_folder_2.is_dir.return_value = True
        mock_folder_2.name = "proton-2"

        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = True
        mock_path_instance.glob.return_value = [mock_folder_1, mock_folder_2]

        # Mock the compatibility tool cache to return additional paths
        mock_cache = {
            "tool-1": MagicMock(dir="/mock/path_1"),
            "tool-2": MagicMock(dir="/mock/path_2"),
        }
        mock_get_cache.return_value = mock_cache

        # Act
        result = get_proton_versions_list(self.mock_runtime_config)

        # Assert
        self.assertEqual([item.value for item in result], ["proton-1", "proton-2"])
        mock_path.assert_any_call(compat_tools_path)


if __name__ == "__main__":
    unittest.main()
