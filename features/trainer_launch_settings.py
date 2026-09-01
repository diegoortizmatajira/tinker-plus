"""Module for enabling and configuring custom trainers or WeMod integration."""

from typing import override

from core import (
    FeatureAction,
    FeatureProvider,
    ProcessRunner,
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

TRAINER_AS_DEBUGGER_PROPERTY = ConfigurationProperty(
    bool,
    "TRAINER_AS_DEBUGGER",
    "Enable trainer as debugger",
    "Allows running the trainer as a debugger for the game process.",
    True,
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
                TRAINER_AS_DEBUGGER_PROPERTY,
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

    def configure_trainer(
        self,
        runtime_configuration: RuntimeConfiguration,
        command: Command,
        as_debugger: bool,
    ) -> None:
        """
        Configures the trainer to run as a debugger if specified.

        Args:
            runtime_configuration (RuntimeConfiguration): The runtime configuration
            to update with the trainer command.
            command (Command): The trainer command to configure.
            as_debugger (bool): Whether to run the trainer as a debugger.
        """
        self.logger.info("Configuring trainer: %s", command.get_full_command())
        if as_debugger:
            self.logger.info("Configuring trainer to run as debugger.")
            runtime_configuration.set_debugger(command)
        else:
            self.logger.info("Trainer will run as forked process.")
            runtime_configuration.add_fork_command(command)
        runtime_configuration.execute_trainers = True

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        """Configures whichever trainer sources are enabled (custom executable,
        WeMod, Cheat Engine) as forked or debugger commands on the runtime
        configuration."""
        as_debugger = TRAINER_AS_DEBUGGER_PROPERTY.get_or_fail(configuration)

        # Check for custom trainer configuration
        custom_trainer = (
            TRAINER_ENABLED_PROPERTY.get(configuration)
            and TRAINER_CUSTOM_EXE_PROPERTY.get(configuration)
            or None
        )
        if custom_trainer:
            trainer_command = Command.from_parts(
                custom_trainer,
                TRAINER_CUSTOM_ARGS_PROPERTY.get(configuration),
                category=CommandCategory.TRAINER,
            )
            self.configure_trainer(runtime_configuration, trainer_command, as_debugger)

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
            self.configure_trainer(
                runtime_configuration,
                Command.from_parts(
                    wemod_path,
                    wemod_args,
                    category=CommandCategory.TRAINER,
                ),
                as_debugger,
            )

        cheat_engine_path = TRAINER_CHEAT_ENGINE_EXE_PROPERTY.get(configuration)
        if cheat_engine_path:
            cheat_engine_file = TRAINER_CHEAT_ENGINE_FILE_PROPERTY.get(configuration)
            if cheat_engine_file or TRAINER_CHEAT_ENGINE_RUN_WITHOUT_FILE_PROPERTY.get(
                configuration
            ):
                cheat_engine_file = (
                    f'"{cheat_engine_file}"' if cheat_engine_file else None
                )
                self.configure_trainer(
                    runtime_configuration,
                    Command.from_parts(
                        cheat_engine_path,
                        cheat_engine_file,
                        category=CommandCategory.TRAINER,
                    ),
                    as_debugger,
                )

        # Set the execute_trainers flag based on the configuration

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
        self.logger.info("Preparing Wine prefix for WeMod integration...")
        winetricks = TRAINER_WEMOD_WINETRICKS_REQUIREMENTS.get(configuration, [])
        self.logger.info("WeMod trainer winetricks: %s", ",".join(winetricks))

        try:
            self.logger.info(
                "Using steam compatibility tool: %s",
                runtime_configuration.steam_compatibility_tool,
            )
            self.logger.info(
                "Using steam game ID: %s", runtime_configuration.get_game_identifier()
            )
            if runtime_configuration.steam_compatibility_tool is None:
                self.logger.error(
                    "Steam compatibility tool not found in environment data."
                )
                return
            installer_command = Command(
                [
                    "/usr/bin/protontricks",
                    runtime_configuration.get_game_identifier(),
                    "dotnet48",
                ]
            )
            dotnet_installer = ProcessRunner.run_chain_command(
                installer_command.get_chain_command(),
                self.logger,
                environment_variables={
                    "PROTON_VERSION": runtime_configuration.steam_compatibility_tool,
                },
                dry_run=runtime_configuration.dry_run,
            )
            if dotnet_installer:
                result = dotnet_installer.wait()
                if result != 0:
                    self.logger.error(
                        "Dotnet 4.8 installer exited with code %d.", result
                    )
                    raise RuntimeError(
                        f"Dotnet 4.8 installer failed with code {result}"
                    )
                self.logger.info("Dotnet 4.8 installer completed successfully.")
        except RuntimeError as e:
            self.logger.error("Failed to prepare Wine prefix for WeMod: %s", e)
            raise
