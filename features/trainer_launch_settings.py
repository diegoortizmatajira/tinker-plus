"""Module for enabling and configuring custom trainers or WeMod integration."""

from typing import override

from core import (
    FeatureAction,
    FeatureProvider,
    ProcessRunner,
    Wine,
)
from defaults import ACTUAL_TPLUS_LOCATION
from model import (
    ConfigurationProperty,
    Command,
    CommandCategory,
    ConfigurationDictionary,
    RuntimeConfiguration,
)

DOTNET48_OFFLINE_INSTALLER = (
    f"{ACTUAL_TPLUS_LOCATION}/redist/NDP48-x86-x64-AllOS-ENU.exe"
)

TRAINER_ENABLED_PROPERTY = ConfigurationProperty(
    bool,
    "TRAINER_ENABLED",
    "Enable running custom trainer",
    "Enables custom trainer launching.",
    True,
)
TRAINER_CUSTOM_EXE_PROPERTY = ConfigurationProperty(
    str,
    "TRAINER_CUSTOM_EXE",
    "Custom trainer executable",
    "Allows selection of a specific trainer excecutable program.",
)

TRAINER_CUSTOM_ARGS_PROPERTY = ConfigurationProperty(
    str,
    "TRAINER_CUSTOM_ARGS",
    "Custom trainer arguments",
    "Allows providing custom args to the trainer program.",
)

TRAINER_WEMOD_ENABLED_PROPERTY = ConfigurationProperty(
    bool,
    "TRAINER_WEMOD_ENABLED",
    "Enable Wemod integration",
    "Enables WeMod integration for trainer launching.",
    False,
)

TRAINER_WEMOD_EXE_PROPERTY = ConfigurationProperty(
    str,
    "TRAINER_WEMOD_EXE",
    "WeMod executable",
    "Specifies the path to the WeMod executable.",
)

TRAINER_WEMOD_OPEN_WITHOUT_GAMEID_PROPERTY = ConfigurationProperty(
    bool,
    "TRAINER_WEMOD_OPEN_WITHOUT_GAMEID",
    "WeMod open without game ID",
    "Specifies whether to open WeMod without a specific game ID.",
    False,
)

TRAINER_WEMOD_GAMEID_PROPERTY = ConfigurationProperty(
    str,
    "TRAINER_WEMOD_GAMEID",
    "WeMod game ID",
    "Specifies the WeMod game ID for the target game.",
)

TRAINER_WEMOD_WINETRICKS_REQUIREMENTS = ConfigurationProperty(
    list,
    "TRAINER_WEMOD_WINETRICKS_REQUIREMENTS",
    "WeMod Winetricks Requirements",
    "Specifies the Winetricks requirements for WeMod integration.",
    ["dotnet48", "dotnetdesktop6"],
)

TRAINER_CHEAT_ENGINE_EXE_PROPERTY = ConfigurationProperty(
    str,
    "TRAINER_CHEAT_ENGINE_EXE",
    "Cheat Engine executable",
    "Specifies the path to the Cheat Engine executable.",
)

TRAINER_CHEAT_ENGINE_FILE_PROPERTY = ConfigurationProperty(
    str,
    "TRAINER_CHEAT_ENGINE_FILE",
    "Cheat Engine file",
    "Specifies the path to the Cheat Engine file to load.",
)

TRAINER_CHEAT_ENGINE_RUN_WITHOUT_FILE_PROPERTY = ConfigurationProperty(
    bool,
    "TRAINER_CHEAT_ENGINE_RUN_WITHOUT_FILE",
    "Cheat Engine run without file",
    "Specifies whether to run Cheat Engine without loading a specific file.",
    False,
)


class TrainerLaunchSettings(FeatureProvider):
    """
    A feature provider for configuring and launching custom trainers or WeMod integration.
    """

    def __init__(self):
        super().__init__(
            "Trainers",
            [
                TRAINER_ENABLED_PROPERTY,
                TRAINER_CUSTOM_EXE_PROPERTY,
                TRAINER_CUSTOM_ARGS_PROPERTY,
                TRAINER_WEMOD_ENABLED_PROPERTY,
                TRAINER_WEMOD_EXE_PROPERTY,
                TRAINER_WEMOD_OPEN_WITHOUT_GAMEID_PROPERTY,
                TRAINER_WEMOD_GAMEID_PROPERTY,
                TRAINER_WEMOD_WINETRICKS_REQUIREMENTS,
                TRAINER_CHEAT_ENGINE_EXE_PROPERTY,
                TRAINER_CHEAT_ENGINE_FILE_PROPERTY,
                TRAINER_CHEAT_ENGINE_RUN_WITHOUT_FILE_PROPERTY,
            ],
            "Trainers",
            actions=[
                FeatureAction(
                    "trainers-prepare-wemod",
                    "Prepare Prefix for WeMod",
                    "Prepare the Wine prefix for WeMod integration.",
                    self.prepare_prefix_for_wemod,
                ),
            ],
        )

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        execute_trainer = False

        # Check for custom trainer configuration
        custom_trainer = (
            TRAINER_ENABLED_PROPERTY.get(configuration)
            and TRAINER_CUSTOM_EXE_PROPERTY.get(configuration)
            or None
        )
        if custom_trainer:
            custom_trainer_args = TRAINER_CUSTOM_ARGS_PROPERTY.get(configuration)
            runtime_configuration.add_fork_command(
                Command.from_parts(
                    custom_trainer,
                    custom_trainer_args,
                    category=CommandCategory.TRAINER,
                )
            )
            execute_trainer = True
            self.logger.info("Custom trainer: %s", custom_trainer)
            self.logger.info("Custom trainer args: %s", custom_trainer_args)

        # Check for WeMod integration
        wemod_path = (
            TRAINER_WEMOD_ENABLED_PROPERTY.get(configuration)
            and TRAINER_WEMOD_EXE_PROPERTY.get(configuration)
            or None
        )
        game_id = TRAINER_WEMOD_GAMEID_PROPERTY.get(configuration)
        if wemod_path and (
            TRAINER_WEMOD_OPEN_WITHOUT_GAMEID_PROPERTY.get(configuration) or game_id
        ):
            wemod_args = (
                f'"wemod://play?titleId={game_id}&gameId={game_id}"'
                if game_id
                else None
            )
            runtime_configuration.add_fork_command(
                Command.from_string(
                    wemod_path,
                    wemod_args,
                    category=CommandCategory.TRAINER,
                )
            )
            execute_trainer = True
            self.logger.info("WeMod trainer: %s", wemod_path)
            self.logger.info("WeMod trainer game id: %s", game_id or "Not specified")

        cheat_engine_path = TRAINER_CHEAT_ENGINE_EXE_PROPERTY.get(configuration)
        if cheat_engine_path:
            cheat_engine_file = TRAINER_CHEAT_ENGINE_FILE_PROPERTY.get(configuration)
            if cheat_engine_file or TRAINER_CHEAT_ENGINE_RUN_WITHOUT_FILE_PROPERTY.get(
                configuration
            ):
                cheat_engine_file = (
                    f'"{cheat_engine_file}"' if cheat_engine_file else None
                )
                runtime_configuration.add_fork_command(
                    Command.from_string(
                        cheat_engine_path,
                        cheat_engine_file,
                        category=CommandCategory.TRAINER,
                    )
                )
                execute_trainer = True
                self.logger.info("Cheat Engine trainer: %s", cheat_engine_path)
                self.logger.info("Cheat Engine file: %s", cheat_engine_file)

        # Set the execute_trainers flag based on the configuration
        runtime_configuration.execute_trainers = execute_trainer

        return runtime_configuration

    def prepare_prefix_for_wemod(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ):
        # pylint: disable=line-too-long
        """
        Prepares the Wine prefix for WeMod integration by adding necessary Winetricks.
        See: https://www.reddit.com/r/SteamDeck/comments/1gtlydp/wemod_a_guide_to_installing/?share_id=utlceK1w5lmQ33fx6jBij&utm_name=iossmf
        """
        winetricks = TRAINER_WEMOD_WINETRICKS_REQUIREMENTS.get(configuration, [])
        self.logger.info("WeMod trainer winetricks: %s", ",".join(winetricks))

        try:
            original_win_version = Wine.get_win_version(
                runtime_configuration, self.logger
            )
            if original_win_version is None:
                self.logger.error(
                    "Could not determine original Windows version in Wine prefix."
                )
                return
            Wine.set_win_version("win7", runtime_configuration, self.logger)
            # Install required Winetricks packages
            succeed = ProcessRunner.run_in_wine_prefix(
                Command.from_string("wine", DOTNET48_OFFLINE_INSTALLER),
                runtime_configuration,
                self.logger,
            )
            if succeed:
                self.logger.info("Dotnet 4.8 installed successfully.")
            else:
                self.logger.error("Dotnet 4.8 installation failed.")
                raise RuntimeError("Dotnet 4.8 installation failed")
            Wine.set_win_version(
                original_win_version, runtime_configuration, self.logger
            )
        except RuntimeError as e:
            self.logger.error("Failed to prepare Wine prefix for WeMod: %s", e)
            raise
