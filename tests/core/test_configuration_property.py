import logging
import unittest

from core.configuration_property import (
    ConfigurationProperty,
    ListItem,
)
from core.configuration_types import AcceptedPropertyTypes, ConfigurationDictionary
from core.runtime_configuration import RuntimeConfiguration


class TestConfigurationProperty(unittest.TestCase):
    def test_get(self):
        properties: list[ConfigurationProperty[AcceptedPropertyTypes]] = [
            ConfigurationProperty(
                str, "STRING_PROPERTY", "A string", "A string property"
            ),
            ConfigurationProperty(
                int, "INT_PROPERTY", "An integer", "An integer property"
            ),
            ConfigurationProperty(
                bool, "BOOL_PROPERTY", "A boolean", "A boolean property"
            ),
            ConfigurationProperty(list, "LIST_PROPERTY", "A list", "A list property"),
        ]
        configuration: ConfigurationDictionary = {
            "STRING_PROPERTY": "test_string",
            "INT_PROPERTY": 42,
            "BOOL_PROPERTY": True,
            "LIST_PROPERTY": ["item1", "item2", "item3"],
        }
        for prop in properties:
            value = prop.get(configuration)
            self.assertIsInstance(value, prop.type_ref)  # type: ignore
            self.assertEqual(value, configuration[prop.name])

    def test_get_defaults(self):
        properties: list[ConfigurationProperty[AcceptedPropertyTypes]] = [
            # Properties without defaults should return None
            ConfigurationProperty(
                str, "STRING_PROPERTY", "A string", "A string property"
            ),
            ConfigurationProperty(
                int, "INT_PROPERTY", "An integer", "An integer property"
            ),
            ConfigurationProperty(
                bool, "BOOL_PROPERTY", "A boolean", "A boolean property"
            ),
            ConfigurationProperty(list, "LIST_PROPERTY", "A list", "A list property"),
            # Properties with defaults should return the default value
            ConfigurationProperty(
                str, "STRING_PROPERTY", "A string", "A string property", "default"
            ),
            ConfigurationProperty(
                int, "INT_PROPERTY", "An integer", "An integer property", 999
            ),
            ConfigurationProperty(
                bool, "BOOL_PROPERTY", "A boolean", "A boolean property", False
            ),
            ConfigurationProperty(
                list, "LIST_PROPERTY", "A list", "A list property", []
            ),
        ]
        configuration: ConfigurationDictionary = {}
        for prop in properties:
            value = prop.get(configuration)
            if prop.default is None:
                self.assertIsNone(value)
            else:
                self.assertIsInstance(value, prop.type_ref)
            self.assertEqual(value, prop.default)

    def test_get_or_fail(self):
        properties: list[ConfigurationProperty[AcceptedPropertyTypes]] = [
            ConfigurationProperty(
                str, "STRING_PROPERTY", "A string", "A string property"
            ),
            ConfigurationProperty(
                int, "INT_PROPERTY", "An integer", "An integer property"
            ),
            ConfigurationProperty(
                bool, "BOOL_PROPERTY", "A boolean", "A boolean property"
            ),
            ConfigurationProperty(list, "LIST_PROPERTY", "A list", "A list property"),
        ]
        configuration: ConfigurationDictionary = {}
        for prop in properties:
            with self.assertRaises(KeyError):
                _ = prop.get_or_fail(configuration)

    def test_get_possible_values(self):
        # Scenario: values provider is set and returns values
        values: list[ListItem[AcceptedPropertyTypes]] = [
            ListItem("value1", "value1"),
            ListItem("value2", "value2"),
        ]
        logger = logging.getLogger("test_logger")

        def values_provider(
            _runtime_configuration: RuntimeConfiguration, _logger: logging.Logger
        ) -> list[ListItem[AcceptedPropertyTypes]]:
            return values

        prop = ConfigurationProperty(
            str,
            name="key",
            display_name="key",
            description="A key",
            values_provider=values_provider,
        )
        runtime_configuration = RuntimeConfiguration.empty()
        self.assertEqual(
            prop.get_possible_values(runtime_configuration, logger), values
        )

        # Scenario: values provider is not set
        prop_no_provider = ConfigurationProperty(
            str, name="key", display_name="key", description="A key"
        )
        self.assertIsNone(
            prop_no_provider.get_possible_values(runtime_configuration, logger)
        )

    def test_translate_to_environment_variable(self):
        runtime_configuration = RuntimeConfiguration.empty()
        logger = logging.getLogger("test_logger")

        # Scenario: Binary property
        prop = ConfigurationProperty(
            bool,
            name="binary_key",
            display_name="binary_key",
            description="Test binary key",
            generated_environment_variable="TEST_BINARY",
        )
        configuration: ConfigurationDictionary = {"binary_key": True}
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
            list[str],
            name="list_key",
            display_name="list_key",
            description="Testing multi-value list key",
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
            str, name="key1", display_name="key1", description="A key", default="value1"
        )
        prop2 = ConfigurationProperty(
            str,
            name="key2",
            display_name="key2",
            description="Another key",
            default="value2",
        )
        prop3 = ConfigurationProperty(
            bool,
            name="key3",
            display_name="key3",
            description="A boolean key",
            default=True,
        )
        configuration: ConfigurationDictionary = {}
        updated_config = ConfigurationProperty.initialize_defaults(
            configuration, [prop1, prop2, prop3]
        )
        self.assertEqual(updated_config["key1"], "value1")
        self.assertEqual(updated_config["key2"], "value2")
        self.assertEqual(updated_config["key3"], True)

        # Scenario: property already in the config remains unchanged
        configuration = {"key1": "overridden_value", "key3": False}
        updated_config = ConfigurationProperty.initialize_defaults(
            configuration, [prop1, prop2, prop3]
        )
        self.assertEqual(updated_config["key1"], "overridden_value")
        self.assertEqual(updated_config["key2"], "value2")
        self.assertEqual(updated_config["key3"], False)


if __name__ == "__main__":
    _ = unittest.main()
