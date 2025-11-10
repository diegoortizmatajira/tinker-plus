from typing import override
from core import FeatureProvider, ConfigurationProperty, RuntimeConfiguration
from core.runtime_configuration import COMMAND_TRAINER, ExecutableCommand

CUSTOM_TRAINER_PROPERTY = ConfigurationProperty(
    "CUSTOM_TRAINER", "Allows selection of a specific trainer excecutable program."
)

CUSTOM_TRAINER_ARGS_PROPERTY = ConfigurationProperty(
    "CUSTOM_TRAINER_ARGS", "Allows providing custom args to the trainer program."
)

WEMOD_ENABLED_PROPERTY = ConfigurationProperty(
    "WEMOD_ENABLED", "Enables WeMod integration for trainer launching."
)

WEMOD_PATH_PROPERTY = ConfigurationProperty(
    "WEMOD_PATH", "Specifies the path to the WeMod executable."
)

WEMOD_WINETRICKS_REQUIREMENTS = ConfigurationProperty(
    "WEMOD_WINETRICKS_REQUIREMENTS",
    "Specifies the Winetricks requirements for WeMod integration.",
    "dotnet48",
)


class TrainerLaunchSettings(FeatureProvider):
    """
    A feature provider for configuring and launching custom trainers or WeMod integration.
    """

    def __init__(self):
        super().__init__(
            [
                CUSTOM_TRAINER_PROPERTY,
                CUSTOM_TRAINER_ARGS_PROPERTY,
                WEMOD_ENABLED_PROPERTY,
                WEMOD_PATH_PROPERTY,
                WEMOD_WINETRICKS_REQUIREMENTS,
            ]
        )

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        execute_trainer = False
        # Check for custom trainer configuration
        custom_trainer = CUSTOM_TRAINER_PROPERTY.get(configuration)
        if custom_trainer:
            custom_trainer_args = CUSTOM_TRAINER_ARGS_PROPERTY.get(configuration)
            runtime_configuration.add_fork_command(
                ExecutableCommand(
                    custom_trainer,
                    custom_trainer_args,
                    COMMAND_TRAINER,
                )
            )
            execute_trainer = True
            self.logger.info("Custom trainer: %s", custom_trainer)
            self.logger.info("Custom trainer args: %s", custom_trainer_args)

        # Check for WeMod integration
        wemod_path = (
            WEMOD_ENABLED_PROPERTY.get(configuration) == "1"
            and WEMOD_PATH_PROPERTY.get(configuration)
            or None
        )
        if wemod_path:
            runtime_configuration.add_fork_command(
                ExecutableCommand(wemod_path, None, COMMAND_TRAINER)
            )
            wemod_winetricks = (
                WEMOD_WINETRICKS_REQUIREMENTS.get(configuration) or ""
            ).split(",")
            runtime_configuration.add_winetricks(wemod_winetricks)
            execute_trainer = True
            self.logger.info("WeMod trainer: %s", wemod_path)
            self.logger.info("WeMod trainer winetricks: %s", ",".join(wemod_winetricks))

        # Set the execute_trainers flag based on the configuration
        runtime_configuration.execute_trainers = execute_trainer
        return runtime_configuration
