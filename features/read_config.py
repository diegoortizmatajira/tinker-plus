from typing import override
from core import ConfigurationProperty, FeatureProvider, RuntimeConfiguration


class ReadConfig(FeatureProvider):
    def __init__(self):
        super().__init__([])

    @override
    def build_configuration(self, sourced_configuration: dict) -> dict:
        return {
            "USE_PROTON": "PROTON_7_0",
            "WEMOD_ENABLED": "1",
            "WEMOD_PATH": "/path/to/wemod/executable",
        }
