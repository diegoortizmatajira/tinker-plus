import unittest
from unittest.mock import MagicMock

from core.config_storage import ConfigStorage
from core.feature_provider import FeatureAction, FeatureProvider
from core.runtime_provider import RuntimeProvider
from model import ConfigurationDictionary, RuntimeConfiguration


class RecordingFeature(FeatureProvider):
    """A FeatureProvider test double that records the order lifecycle hooks are called in."""

    def __init__(self, name: str, calls: list[tuple[str, str]], extra_config=None):
        super().__init__(name, [])
        self.calls = calls
        self.extra_config = extra_config or {}

    def build_configuration(
        self,
        sourced_configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ) -> ConfigurationDictionary:
        self.calls.append((self.name, "build_configuration"))
        merged = dict(sourced_configuration)
        merged.update(self.extra_config)
        return merged

    def override_configuration(
        self,
        sourced_configuration: ConfigurationDictionary,
        _runtime_configuration: RuntimeConfiguration,
    ) -> ConfigurationDictionary:
        self.calls.append((self.name, "override_configuration"))
        return sourced_configuration

    def apply_configuration(
        self,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        self.calls.append((self.name, "apply_configuration"))
        return runtime_configuration

    def before_execution(self, _configuration, _runtime_configuration):
        self.calls.append((self.name, "before_execution"))

    def execute_in_pipeline(self, _configuration, _runtime_configuration):
        self.calls.append((self.name, "execute_in_pipeline"))

    def wait_for_completion(self, _configuration, _runtime_configuration):
        self.calls.append((self.name, "wait_for_completion"))

    def after_execution(self, _configuration, _runtime_configuration):
        self.calls.append((self.name, "after_execution"))


class TestRuntimeProvider(unittest.TestCase):
    def _make_provider(self, features: list[FeatureProvider]) -> RuntimeProvider:
        storage = MagicMock(spec=ConfigStorage)
        return RuntimeProvider(["game.exe"], True, features, storage)

    def test_init_starts_with_empty_configuration(self):
        provider = self._make_provider([])
        self.assertEqual(provider.configuration, {})
        self.assertTrue(provider.runtime_configuration.dry_run)

    def test_build_configuration_merges_each_features_defaults(self):
        calls: list[tuple[str, str]] = []
        feature_a = RecordingFeature("A", calls, extra_config={"KEY_A": "a"})
        feature_b = RecordingFeature("B", calls, extra_config={"KEY_B": "b"})
        provider = self._make_provider([feature_a, feature_b])
        provider.build_configuration()
        self.assertEqual(provider.configuration, {"KEY_A": "a", "KEY_B": "b"})

    def test_build_configuration_calls_build_then_override_for_all_features(self):
        calls: list[tuple[str, str]] = []
        feature_a = RecordingFeature("A", calls)
        feature_b = RecordingFeature("B", calls)
        provider = self._make_provider([feature_a, feature_b])
        provider.build_configuration()
        self.assertEqual(
            calls,
            [
                ("A", "build_configuration"),
                ("B", "build_configuration"),
                ("A", "override_configuration"),
                ("B", "override_configuration"),
            ],
        )

    def test_build_configuration_pre_apply_applies_configuration(self):
        calls: list[tuple[str, str]] = []
        # extra_config ensures self.configuration differs from the initial (empty)
        # last_applied_configuration, so the change-detection in
        # __apply_feature_configurations doesn't short-circuit the apply.
        feature = RecordingFeature("A", calls, extra_config={"KEY": "value"})
        provider = self._make_provider([feature])
        provider.build_configuration(pre_apply_configuration=True)
        self.assertIn(("A", "apply_configuration"), calls)

    def test_build_configuration_without_pre_apply_does_not_apply(self):
        calls: list[tuple[str, str]] = []
        feature = RecordingFeature("A", calls)
        provider = self._make_provider([feature])
        provider.build_configuration()
        self.assertNotIn(("A", "apply_configuration"), calls)

    def test_run_executes_stages_in_order_across_all_features(self):
        calls: list[tuple[str, str]] = []
        feature_a = RecordingFeature("A", calls, extra_config={"KEY": "value"})
        feature_b = RecordingFeature("B", calls)
        provider = self._make_provider([feature_a, feature_b])
        provider.build_configuration()
        calls.clear()
        provider.run()
        self.assertEqual(
            calls,
            [
                ("A", "apply_configuration"),
                ("B", "apply_configuration"),
                ("A", "before_execution"),
                ("B", "before_execution"),
                ("A", "execute_in_pipeline"),
                ("B", "execute_in_pipeline"),
                ("A", "wait_for_completion"),
                ("B", "wait_for_completion"),
                ("A", "after_execution"),
                ("B", "after_execution"),
            ],
        )

    def test_run_sets_execute_trainers_flag(self):
        provider = self._make_provider([])
        provider.run(run_with_trainers=False)
        self.assertFalse(provider.runtime_configuration.execute_trainers)
        provider.run(run_with_trainers=True)
        self.assertTrue(provider.runtime_configuration.execute_trainers)

    def test_apply_feature_configurations_skips_when_unchanged(self):
        calls: list[tuple[str, str]] = []
        feature = RecordingFeature("A", calls, extra_config={"KEY": "value"})
        provider = self._make_provider([feature])
        provider.build_configuration(pre_apply_configuration=True)
        calls.clear()
        # configuration hasn't changed since the pre-apply above, so run()'s
        # own apply_feature_configurations pass should be a no-op.
        provider.run()
        self.assertNotIn(("A", "apply_configuration"), calls)

    def test_apply_feature_configurations_reapplies_when_configuration_changes(self):
        calls: list[tuple[str, str]] = []
        feature = RecordingFeature("A", calls, extra_config={"KEY": "value"})
        provider = self._make_provider([feature])
        provider.build_configuration(pre_apply_configuration=True)
        calls.clear()
        provider.configuration["NEW_KEY"] = "changed"
        provider.run()
        self.assertIn(("A", "apply_configuration"), calls)

    def test_run_action_applies_configuration_and_invokes_action(self):
        provider = self._make_provider([])
        received: list[ConfigurationDictionary] = []
        action = FeatureAction(
            "alias", "Name", "Description", lambda cfg, _rt: received.append(cfg)
        )
        provider.run_action(action)
        self.assertEqual(len(received), 1)

    def test_get_available_actions_collects_from_all_features(self):
        action_a = FeatureAction("a", "A", "desc", lambda cfg, rt: None)
        action_b = FeatureAction("b", "B", "desc", lambda cfg, rt: None)

        class FeatureWithActions(FeatureProvider):
            def __init__(self, name: str, actions: list[FeatureAction]):
                super().__init__(name, [], actions=actions)

        feature_a = FeatureWithActions("A", [action_a])
        feature_b = FeatureWithActions("B", [action_b])
        provider = self._make_provider([feature_a, feature_b])
        self.assertEqual(provider.get_available_actions(), [action_a, action_b])


if __name__ == "__main__":
    _ = unittest.main()
