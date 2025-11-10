"""
A feature provider for executing the main game command and any forked commands
"""

from typing import override
from core import FeatureProvider, RuntimeConfiguration


class GameRunner(FeatureProvider):
    """
    A feature provider for executing the main game command and any forked
    commands using the runtime configuration.
    """

    def __init__(self):
        super().__init__([])

    @override
    def execute_in_pipeline(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ):
        # TODO: Execute commands and forked commands
        pass
