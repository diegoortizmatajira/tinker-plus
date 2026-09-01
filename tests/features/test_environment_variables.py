import unittest

from features.environment_variables import EnvironmentVariables
from model import RuntimeConfiguration


class TestEnvironmentVariablesApplyConfiguration(unittest.TestCase):
    def setUp(self):
        self.feature = EnvironmentVariables()
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_sets_environment_variable_from_key_value_pair(self):
        self.feature.apply_configuration(
            {"ENVIRONMENT_VARIABLES": ["FOO=bar"]}, self.runtime_configuration
        )
        self.assertEqual(
            self.runtime_configuration.environment_variables, {"FOO": "bar"}
        )

    def test_sets_multiple_environment_variables(self):
        self.feature.apply_configuration(
            {"ENVIRONMENT_VARIABLES": ["FOO=bar", "BAZ=qux"]},
            self.runtime_configuration,
        )
        self.assertEqual(
            self.runtime_configuration.environment_variables,
            {"FOO": "bar", "BAZ": "qux"},
        )

    def test_ignores_entries_without_equals_sign(self):
        self.feature.apply_configuration(
            {"ENVIRONMENT_VARIABLES": ["NOEQUALSIGN"]}, self.runtime_configuration
        )
        self.assertIsNone(self.runtime_configuration.environment_variables)

    def test_handles_value_containing_equals_sign(self):
        self.feature.apply_configuration(
            {"ENVIRONMENT_VARIABLES": ["KEY=a=b"]}, self.runtime_configuration
        )
        self.assertEqual(
            self.runtime_configuration.environment_variables, {"KEY": "a=b"}
        )

    def test_defaults_to_no_variables_when_not_configured(self):
        self.feature.apply_configuration({}, self.runtime_configuration)
        self.assertIsNone(self.runtime_configuration.environment_variables)

    def test_returns_the_runtime_configuration(self):
        result = self.feature.apply_configuration({}, self.runtime_configuration)
        self.assertIs(result, self.runtime_configuration)


class TestEnvironmentVariablesExecuteInPipeline(unittest.TestCase):
    def setUp(self):
        self.feature = EnvironmentVariables()
        self.runtime_configuration = RuntimeConfiguration.empty()

    def test_logs_each_configured_environment_variable(self):
        self.runtime_configuration.environment_variables = {"A": "1", "B": "2"}
        with self.assertLogs(level="INFO") as captured:
            self.feature.execute_in_pipeline({}, self.runtime_configuration)
        joined = "\n".join(captured.output)
        self.assertIn("A=1", joined)
        self.assertIn("B=2", joined)

    def test_does_not_raise_when_no_environment_variables_set(self):
        self.runtime_configuration.environment_variables = None
        # Should simply do nothing without raising.
        self.feature.execute_in_pipeline({}, self.runtime_configuration)


if __name__ == "__main__":
    _ = unittest.main()
