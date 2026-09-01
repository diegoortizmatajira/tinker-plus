"""General runtime feature provider."""

from typing import override

from core import (
    FeatureProvider,
    SteamParser,
    SteamUtil,
)
from model import (
    Command,
    CommandCategory,
    CompatToolInfo,
    RuntimeConfiguration,
    SteamEnvironmentData,
    ConfigurationDictionary,
    ConfigurationProperty,
)
from repositories import CompatToolInfoRepository

GENERAL_LOG_INDIVIDUAL_EXE_PROPERTY = ConfigurationProperty(
    bool,
    "GENERAL_LOG_INDIVIDUAL_EXE",
    "Log Individual Executables",
    "If set to True, logs each individual executable that is run in is own file.",
    default=False,
)


class GeneralRuntime(FeatureProvider):
    """
    A feature provider that applies general runtime configurations.

    This class manages the integration of generic runtime settings,
    particularly for logging executable commands, by interacting
    with configuration properties.
    """

    def __init__(self):
        super().__init__(
            "General Runtime",
            [
                GENERAL_LOG_INDIVIDUAL_EXE_PROPERTY,
            ],
            "General",
        )

    @override
    def build_configuration(
        self,
        sourced_configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> ConfigurationDictionary:
        """Parses the Steam environment/command line, populates the runtime
        configuration's Steam environment data, game info, and game executable
        command, and refreshes the compatibility tool cache."""
        result = super().build_configuration(
            sourced_configuration, runtime_configuration
        )
        # Parse Steam Environment Variables and original command line
        data = SteamEnvironmentData()
        SteamParser.parse(
            data, " ".join(runtime_configuration.original_command), self.logger
        )
        if SteamParser.has_valid_data(data):
            SteamParser.save(
                data,
                runtime_configuration.dry_run,
                self.logger,
            )
        runtime_configuration.steam_environment_data = data
        # Handle Steam Compatibility Tool caching
        if data.cmd_steam_compatibility_tool:
            compat_tool_info = CompatToolInfoRepository.from_cache(
                data.cmd_steam_compatibility_tool, self.logger
            )
            if not compat_tool_info:
                compat_tool_info = CompatToolInfo(
                    name=data.cmd_steam_compatibility_tool,
                    dir=data.cmd_steam_compatibility_tools_path or "",
                )
                CompatToolInfoRepository.put_in_cache(compat_tool_info, self.logger)
        _ = CompatToolInfoRepository.scan_and_populate_cache(
            self.logger, runtime_configuration
        )
        # Sets the default prefix path if Steam compatibility data path is available
        if data.steam_compat_data_path:
            runtime_configuration.prefix_path = f"{data.steam_compat_data_path}/pfx"

        runtime_configuration.game_info = SteamUtil.get_game_info(
            runtime_configuration, self.logger
        )
        runtime_configuration.game_executable_command = Command.from_parts(
            runtime_configuration.steam_environment_data.cmd_steam_game_exe or "echo",
            runtime_configuration.steam_environment_data.cmd_steam_game_args,
            cwd=runtime_configuration.steam_environment_data.steam_compat_install_path,
            category=CommandCategory.GAME,
        )
        return result

    @override
    def apply_configuration(
        self,
        _configuration: ConfigurationDictionary,
        runtime_configuration: RuntimeConfiguration,
    ) -> RuntimeConfiguration:
        """Applies the `GENERAL_LOG_INDIVIDUAL_EXE` setting to the runtime
        configuration's `log_executable_commands` flag."""
        runtime_configuration.log_executable_commands = (
            GENERAL_LOG_INDIVIDUAL_EXE_PROPERTY.get(_configuration, False)
        )
        self.logger.info(
            "Individual executable logging is set to: %s",
            runtime_configuration.log_executable_commands,
        )
        return runtime_configuration
