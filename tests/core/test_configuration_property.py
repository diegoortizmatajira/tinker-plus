import unittest
from core.configuration_property import ConfigurationProperty


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

    def test_get_possible_values(self):
        # Scenario: values provider is set and returns values
        def values_provider():
            return ["value1", "value2"]

        prop = ConfigurationProperty(
            name="key", description="A key", values_provider=values_provider
        )
        self.assertEqual(prop.get_possible_values(), ["value1", "value2"])

        # Scenario: values provider is not set
        prop_no_provider = ConfigurationProperty(name="key", description="A key")
        self.assertIsNone(prop_no_provider.get_possible_values())

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
