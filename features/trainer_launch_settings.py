"""Module for enabling and configuring custom trainers or WeMod integration."""

from typing import override
from core import (
    FeatureProvider,
    ConfigurationProperty,
    RuntimeConfiguration,
    process_runner,
)
from core.configuration_types import ConfigurationDictionary
from core.defaults import ACTUAL_TPLUS_LOCATION
from core.feature_provider import FeatureAction
from core.runtime_configuration import COMMAND_TRAINER, ExecutableCommand

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
TRAINER_EXE_PROPERTY = ConfigurationProperty(
    str,
    "TRAINER_EXE",
    "Custom trainer executable",
    "Allows selection of a specific trainer excecutable program.",
)

TRAINER_ARGS_PROPERTY = ConfigurationProperty(
    str,
    "TRAINER_ARGS",
    "Custom trainer arguments",
    "Allows providing custom args to the trainer program.",
)

WEMOD_ENABLED_PROPERTY = ConfigurationProperty(
    bool,
    "WEMOD_ENABLED",
    "Enable Wemod integration",
    "Enables WeMod integration for trainer launching.",
    False,
)

WEMOD_EXE_PROPERTY = ConfigurationProperty(
    str,
    "WEMOD_EXE",
    "WeMod executable",
    "Specifies the path to the WeMod executable.",
)

WEMOD_OPEN_WITHOUT_GAMEID_PROPERTY = ConfigurationProperty(
    bool,
    "WEMOD_OPEN_WITHOUT_GAMEID",
    "WeMod open without game ID",
    "Specifies whether to open WeMod without a specific game ID.",
    False,
)

WEMOD_GAMEID_PROPERTY = ConfigurationProperty(
    str,
    "WEMOD_GAMEID",
    "WeMod game ID",
    "Specifies the WeMod game ID for the target game.",
)

WEMOD_WINETRICKS_REQUIREMENTS = ConfigurationProperty(
    list,
    "WEMOD_WINETRICKS_REQUIREMENTS",
    "WeMod Winetricks Requirements",
    "Specifies the Winetricks requirements for WeMod integration.",
    ["dotnet48", "dotnetdesktop6"],
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
                TRAINER_EXE_PROPERTY,
                TRAINER_ARGS_PROPERTY,
                WEMOD_ENABLED_PROPERTY,
                WEMOD_EXE_PROPERTY,
                WEMOD_OPEN_WITHOUT_GAMEID_PROPERTY,
                WEMOD_GAMEID_PROPERTY,
                WEMOD_WINETRICKS_REQUIREMENTS,
            ],
            "Additional Tools",
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
            and TRAINER_EXE_PROPERTY.get(configuration)
            or None
        )
        if custom_trainer:
            custom_trainer_args = TRAINER_ARGS_PROPERTY.get(configuration)
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
            WEMOD_ENABLED_PROPERTY.get(configuration)
            and WEMOD_EXE_PROPERTY.get(configuration)
            or None
        )
        game_id = WEMOD_GAMEID_PROPERTY.get(configuration)
        if wemod_path and (
            WEMOD_OPEN_WITHOUT_GAMEID_PROPERTY.get(configuration) or game_id
        ):
            wemod_args = (
                f'"wemod://play?titleId={game_id}&gameId={game_id}"'
                if game_id
                else None
            )
            runtime_configuration.add_fork_command(
                ExecutableCommand(
                    wemod_path,
                    wemod_args,
                    COMMAND_TRAINER,
                )
            )
            execute_trainer = True
            self.logger.info("WeMod trainer: %s", wemod_path)
            self.logger.info("WeMod trainer game id: %s", game_id or "Not specified")

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
        winetricks = WEMOD_WINETRICKS_REQUIREMENTS.get(configuration, [])
        self.logger.info("WeMod trainer winetricks: %s", ",".join(winetricks))

        def set_win_version(version: str, description: str):
            succeed = process_runner.run_in_wine_prefix(
                ExecutableCommand("winecfg", f"/v {version}"),
                runtime_configuration,
                self.logger,
            )
            if succeed:
                self.logger.info("%s mode set successfully.", description)
            else:
                self.logger.error("%s mode setting failed.", description)
                raise RuntimeError("Winecfg failed")

        try:
            set_win_version("win7", "Use Windows 7")
            # Install required Winetricks packages
            succeed = process_runner.run_in_wine_prefix(
                ExecutableCommand("wine", DOTNET48_OFFLINE_INSTALLER),
                runtime_configuration,
                self.logger,
            )
            if succeed:
                self.logger.info("Dotnet 4.8 installed successfully.")
            else:
                self.logger.error("Dotnet 4.8 installation failed.")
                raise RuntimeError("Dotnet 4.8 installation failed")
            set_win_version("win10", "Use Windows 10")
        except RuntimeError as e:
            self.logger.error("Failed to prepare Wine prefix for WeMod: %s", e)
            raise
