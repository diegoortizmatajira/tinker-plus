"""
Unit tests for the ProtonSelection class.
"""

import unittest
from unittest.mock import MagicMock

from core.runtime_configuration import RuntimeConfiguration
from features.proton_selection import ProtonSelection


class TestProtonSelection(unittest.TestCase):
    """ Unit tests for the ProtonSelection feature provider. """

    def setUp(self):
        """ Prepare the test environment by initializing ProtonSelection. """
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

        # Apply configuration
        with self.assertRaises(KeyError):
            self.proton_selection.apply_configuration(
                configuration, runtime_configuration
            )

    def test_apply_configuration_with_empty_string(self):
        """
        Test that apply_configuration sets the USE_PROTON value to an empty
        string when provided empty input.
        """
        # Mock input configuration and runtime configuration
        configuration = {"USE_PROTON": ""}
        runtime_configuration = MagicMock(spec=RuntimeConfiguration)

        # Apply configuration
        updated_runtime_config = self.proton_selection.apply_configuration(
            configuration, runtime_configuration
        )

        # Verify the USE_PROTON is set to an empty string
        self.assertEqual(updated_runtime_config.use_proton, "")


if __name__ == "__main__":
    unittest.main()

