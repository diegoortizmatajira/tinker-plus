import logging
import unittest

from core.configuration_property import (
    BINARY_PROPERTY,
    MULTIVALUELIST_PROPERTY,
    ConfigurationProperty,
    ListItem,
)
from core.game_info import GameInfo
from core.runtime_configuration import RuntimeConfiguration


class TestConfigurationProperty(unittest.TestCase):
    def test_get(self):
        # Scenario: property exists in the configuration
        prop = ConfigurationProperty(
            name="key", description="A key", default="default_value"
        )
        configuration = {"key": "value"}
        self.assertEqual(prop.get(configuration), "value")

        # Scenario: property does not exist, default is returned
        configuration = {}
        self.assertEqual(prop.get(configuration), "default_value")

        # Scenario: property does not exist, no default set
        prop_no_default = ConfigurationProperty(name="key", description="A key")
        self.assertIsNone(prop_no_default.get(configuration))

    def test_get_or_fail(self):
        # Scenario: property exists in the configuration
        prop = ConfigurationProperty(name="key", description="A key")
        configuration = {"key": "value"}
        self.assertEqual(prop.get_or_fail(configuration), "value")

        # Scenario: property does not exist, but default is set
        prop_with_default = ConfigurationProperty(
            name="key", description="A key", default="default_value"
        )
        configuration = {}
        self.assertEqual(prop_with_default.get_or_fail(configuration), "default_value")

        # Scenario: property does not exist and no default is set
        prop_no_default = ConfigurationProperty(name="key", description="A key")
        configuration = {}
        with self.assertRaises(KeyError):
            prop_no_default.get_or_fail(configuration)

    def test_get_boolean(self):
        # Scenario: valid boolean value
        prop = ConfigurationProperty(name="key", description="A key")
        configuration = {"key": True}
        self.assertTrue(prop.get_boolean(configuration))

        # Scenario: value does not exist
        configuration = {}
        self.assertIsNone(prop.get_boolean(configuration))

        # Scenario: invalid type for boolean
        configuration = {"key": "not_a_boolean"}
        with self.assertRaises(TypeError):
            prop.get_boolean(configuration)

    def test_get_string(self):
        # Scenario: valid string value
        prop = ConfigurationProperty(name="key", description="A key")
        configuration = {"key": "string_value"}
        self.assertEqual(prop.get_string(configuration), "string_value")

        # Scenario: value does not exist
        configuration = {}
        self.assertIsNone(prop.get_string(configuration))

        # Scenario: invalid type for string
        configuration = {"key": 12345}
        with self.assertRaises(TypeError):
            prop.get_string(configuration)

    def test_get_string_list(self):
        # Scenario: valid string list
        prop = ConfigurationProperty(name="key", description="A key")
        configuration = {"key": ["item1", "item2"]}
        self.assertEqual(prop.get_string_list(configuration), ["item1", "item2"])

        # Scenario: value does not exist
        configuration = {}
        self.assertIsNone(prop.get_string_list(configuration))

        # Scenario: invalid type for string list
        configuration = {"key": "not_a_list"}
        with self.assertRaises(TypeError):
            prop.get_string_list(configuration)

    def test_get_possible_values(self):
        # Scenario: values provider is set and returns values
        values = [ListItem("value1", "value1"), ListItem("value2", "value2")]

        def values_provider(_):
            return values

        prop = ConfigurationProperty(
            name="key", description="A key", values_provider=values_provider
        )
        runtime_configuration = RuntimeConfiguration([], GameInfo.empty(), True)
        self.assertEqual(prop.get_possible_values(runtime_configuration), values)

        # Scenario: values provider is not set
        prop_no_provider = ConfigurationProperty(name="key", description="A key")
        self.assertIsNone(prop_no_provider.get_possible_values(runtime_configuration))

    def test_translate_to_environment_variable(self):
        runtime_configuration = RuntimeConfiguration([], GameInfo.empty(), True)
        logger = logging.getLogger("test_logger")

        # Scenario: Binary property
        prop = ConfigurationProperty(
            name="binary_key",
            description="Test binary key",
            type=BINARY_PROPERTY,
            generated_environment_variable="TEST_BINARY",
        )
        configuration = {"binary_key": True}
        prop.translate_to_environment_variable(
            configuration, runtime_configuration, logger
        )
        self.assertEqual(
            runtime_configuration.environment_variables
            and runtime_configuration.environment_variables.get("TEST_BINARY"),
            "1",
        )

        # Scenario: Multivalue list property
        prop = ConfigurationProperty(
            name="list_key",
            description="Testing multi-value list key",
            type=MULTIVALUELIST_PROPERTY,
            generated_environment_variable="TEST_LIST",
        )
        configuration = {"list_key": ["value1", "value2"]}
        prop.translate_to_environment_variable(
            configuration, runtime_configuration, logger
        )
        self.assertIsNotNone(runtime_configuration.environment_variables)
        self.assertEqual(
            runtime_configuration.environment_variables
            and runtime_configuration.environment_variables.get("TEST_LIST"),
            "value1,value2",
        )

    def test_initialize_defaults(self):
        # Scenario: properties with defaults initialize the configuration
        prop1 = ConfigurationProperty(
            name="key1", description="A key", default="value1"
        )
        prop2 = ConfigurationProperty(
            name="key2", description="Another key", default="value2"
        )
        configuration = {}
        updated_config = ConfigurationProperty.initialize_defaults(
            configuration, [prop1, prop2]
        )
        self.assertEqual(updated_config["key1"], "value1")
        self.assertEqual(updated_config["key2"], "value2")

        # Scenario: property already in the config remains unchanged
        configuration = {"key1": "overridden_value"}
        updated_config = ConfigurationProperty.initialize_defaults(
            configuration, [prop1]
        )
        self.assertEqual(updated_config["key1"], "overridden_value")


if __name__ == "__main__":
    unittest.main()
