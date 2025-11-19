"""Module for enabling and configuring custom trainers or WeMod integration."""

from typing import override
from core import FeatureProvider, ConfigurationProperty, RuntimeConfiguration
from core.runtime_configuration import COMMAND_TRAINER, ExecutableCommand

TRAINER_EXE_PROPERTY = ConfigurationProperty(
    "TRAINER_EXE", "Allows selection of a specific trainer excecutable program."
)

TRAINER_ARGS_PROPERTY = ConfigurationProperty(
    "TRAINER_ARGS", "Allows providing custom args to the trainer program."
)

WEMOD_ENABLED_PROPERTY = ConfigurationProperty(
    "WEMOD_ENABLED", "Enables WeMod integration for trainer launching.", False
)

WEMOD_EXE_PROPERTY = ConfigurationProperty(
    "WEMOD_EXE", "Specifies the path to the WeMod executable."
)

WEMOD_GAMEID_PROPERTY = ConfigurationProperty(
    "WEMOD_GAMEID", "Specifies the WeMod game ID for the target game."
)
WEMOD_WINETRICKS_REQUIREMENTS = ConfigurationProperty(
    "WEMOD_WINETRICKS_REQUIREMENTS",
    "Specifies the Winetricks requirements for WeMod integration.",
    ["dotnet48"],
)


class TrainerLaunchSettings(FeatureProvider):
    """
    A feature provider for configuring and launching custom trainers or WeMod integration.
    """

    def __init__(self):
        super().__init__(
            [
                TRAINER_EXE_PROPERTY,
                TRAINER_ARGS_PROPERTY,
                WEMOD_ENABLED_PROPERTY,
                WEMOD_EXE_PROPERTY,
                WEMOD_GAMEID_PROPERTY,
                WEMOD_WINETRICKS_REQUIREMENTS,
            ]
        )

    @override
    def apply_configuration(
        self, configuration: dict, runtime_configuration: RuntimeConfiguration
    ) -> RuntimeConfiguration:
        execute_trainer = False
        # Check for custom trainer configuration
        custom_trainer = TRAINER_EXE_PROPERTY.get_string(configuration)
        if custom_trainer:
            custom_trainer_args = TRAINER_ARGS_PROPERTY.get_string(configuration)
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
            WEMOD_ENABLED_PROPERTY.get_boolean(configuration)
            and WEMOD_EXE_PROPERTY.get_string(configuration)
            or None
        )
        if wemod_path:
            game_id = WEMOD_GAMEID_PROPERTY.get_string(configuration)
            wemod_args = (
                f"wemod://play?titleId={game_id}&gameId={game_id}" if game_id else None
            )
            runtime_configuration.add_fork_command(
                ExecutableCommand(
                    wemod_path,
                    wemod_args,
                    COMMAND_TRAINER,
                )
            )
            wemod_winetricks = (
                WEMOD_WINETRICKS_REQUIREMENTS.get_string_list(configuration) or []
            )
            runtime_configuration.add_winetricks(wemod_winetricks)
            execute_trainer = True
            self.logger.info("WeMod trainer: %s", wemod_path)
            self.logger.info("WeMod trainer game id: %s", game_id or "Not specified")
            self.logger.info("WeMod trainer winetricks: %s", ",".join(wemod_winetricks))

        # Set the execute_trainers flag based on the configuration
        runtime_configuration.execute_trainers = execute_trainer
        return runtime_configuration
