"""Feature provider for Steam tools and wrappers."""

from typing import override
from core import FeatureProvider
from model import (
    Command,
    ConfigurationProperty,
    RuntimeConfiguration,
    CommandWrapper,
    ConfigurationDictionary,
)

STEAM_USE_WRAPPER_PROPERTY = ConfigurationProperty(
    bool,
    "STEAM_USE_WRAPPER",
    "Use Steam Wrapper",
    "Enables the use of Steam wrapper for Steam games when set to 'True'.",
    default=False,
)

STEAM_USE_SNIPER_PROPERTY = ConfigurationProperty(
    bool,
    "STEAM_USE_SNIPER",
    "Use Steam Sniper",
    "Enables the use of Sniper for Steam games when set to 'True'.",
    default=True,
)

STEAM_USE_REAPER_PROPERTY = ConfigurationProperty(
    bool,
    "STEAM_USE_REAPER",
    "Use Steam Reaper",
    "Enables the use of Reaper for Steam games when set to 'True'.",
    default=True,
)

STEAM_DEFAULT_WRAPPER_COMMAND_PROPERTY = ConfigurationProperty(
    str,
    "STEAM_DEFAULT_WRAPPER_COMMAND",
    "Default Steam Wrapper Command",
    "Specifies the default command to use for the Steam wrapper if none is set.",
    default="ubuntu12_32/steam-launch-wrapper",
)

STEAM_DEFAULT_SNIPER_COMMAND_PROPERTY = ConfigurationProperty(
    str,
    "STEAM_DEFAULT_SNIPER_COMMAND",
    "Default Steam Sniper Command",
    "Specifies the default command to use for Steam Sniper if none is set.",
    default="steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun",
)
STEAM_DEFAULT_REAPER_COMMAND_PROPERTY = ConfigurationProperty(
    str,
    "STEAM_DEFAULT_REAPER_COMMAND",
    "Default Steam Reaper Command",
    "Specifies the default command to use for Steam Reaper if none is set.",
    default="ubuntu12_32/reaper",
)


class SteamTools(FeatureProvider):
    """
    A feature provider for Steam tools that manages the application of
    configuration settings related to different Steam wrappers and tools.

    SteamTools enables the management of specific pipeline wrappers like
    Sniper, Reaper, and a general Steam wrapper based on configuration
    properties provided at runtime.
    """

    def __init__(self):
        super().__init__(
            "Steam Tools",
            [
                STEAM_USE_WRAPPER_PROPERTY,
                STEAM_USE_REAPER_PROPERTY,
                STEAM_USE_SNIPER_PROPERTY,
                STEAM_DEFAULT_WRAPPER_COMMAND_PROPERTY,
                STEAM_DEFAULT_SNIPER_COMMAND_PROPERTY,
                STEAM_DEFAULT_REAPER_COMMAND_PROPERTY,
            ],
            "Pipeline",
        )

    @override
    def apply_configuration(
        self,
        configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        steam_base_folder = (
            runtime_configuration.steam_environment_data.steam_base_folder
        )
        # Load default commands if not already set
        if not runtime_configuration.steam_environment_data.cmd_steam_wrapper:
            runtime_configuration.steam_environment_data.cmd_steam_wrapper = f"{steam_base_folder}/{STEAM_DEFAULT_WRAPPER_COMMAND_PROPERTY.get(configuration)}"
            self.logger.info(
                "Restored default Steam wrapper command as it was not set by runtime provider."
            )
        self.logger.info(
            "Steam Launch Wrapper: %s",
            runtime_configuration.steam_environment_data.cmd_steam_wrapper,
        )
        if not runtime_configuration.steam_environment_data.cmd_steam_sniper:
            runtime_configuration.steam_environment_data.cmd_steam_sniper = f"{steam_base_folder}/{STEAM_DEFAULT_SNIPER_COMMAND_PROPERTY.get(configuration)}"
            self.logger.info(
                "Restored default Steam Sniper command as it was not set by runtime provider."
            )
        self.logger.info(
            "Steam Sniper Command: %s",
            runtime_configuration.steam_environment_data.cmd_steam_sniper,
        )
        if not runtime_configuration.steam_environment_data.cmd_steam_reaper:
            runtime_configuration.steam_environment_data.cmd_steam_reaper = f"{steam_base_folder}/{STEAM_DEFAULT_REAPER_COMMAND_PROPERTY.get(configuration)}"
            self.logger.info(
                "Restored default Steam Reaper command as it was not set by runtime provider."
            )
        self.logger.info(
            "Steam Reaper Command: %s",
            runtime_configuration.steam_environment_data.cmd_steam_reaper,
        )
        # Apply the Steam wrapper
        if (
            STEAM_USE_WRAPPER_PROPERTY.get(configuration)
            and runtime_configuration.steam_environment_data.cmd_steam_wrapper
        ):
            self.logger.info("Enabling Steam wrapper.")
            runtime_configuration.add_pipeline_wrapper(
                CommandWrapper(
                    lambda cmd, rtm_cfg: Command(
                        [
                            Command.from_string(
                                rtm_cfg.steam_environment_data.cmd_steam_wrapper or ""
                            ),
                            "--",
                            cmd,
                        ]
                    )
                )
            )
        # Apply the Reaper (After Wrapper)
        if (
            STEAM_USE_REAPER_PROPERTY.get(configuration)
            and runtime_configuration.steam_environment_data.cmd_steam_reaper
        ):
            self.logger.info("Enabling Steam Reaper wrapper.")

            def reaper_wrapper(cmd: Command, rtm_cfg: RuntimeConfiguration) -> Command:
                args = ["--"]
                if rtm_cfg.get_game_identifier():
                    args = [
                        "SteamLaunch",
                        f"AppId={rtm_cfg.get_game_identifier()}",
                        "--",
                    ]
                return Command(
                    [
                        Command.from_string(
                            rtm_cfg.steam_environment_data.cmd_steam_reaper or ""
                        )
                    ]
                    + args
                    + [cmd]
                )

            runtime_configuration.add_pipeline_wrapper(
                CommandWrapper(
                    wrapper=reaper_wrapper,
                )
            )

        # Apply the Sniper (After Reaper)
        if (
            STEAM_USE_SNIPER_PROPERTY.get(configuration)
            and runtime_configuration.steam_environment_data.cmd_steam_sniper
        ):
            self.logger.info("Enabling Steam Sniper wrapper.")
            runtime_configuration.add_pipeline_wrapper(
                CommandWrapper(
                    lambda cmd, rtm_cfg: Command(
                        [
                            Command.from_string(
                                rtm_cfg.steam_environment_data.cmd_steam_sniper or ""
                            ),
                            "--",
                            cmd,
                        ]
                    )
                )
            )
        return runtime_configuration
