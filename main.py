"""
Main entry point for the Tinker-Plus application.
"""

import logging
import os
from pathlib import Path
import shutil
import sys
import argparse
from core import LogFactory
from core.config_storage import ConfigStorage
from core.defaults import TPLUS_BIN_LOCATION, TPLUS_COMPATIBILITY_TOOL_DIR
from core.file_operations import create_symbolic_link
from core.runtime_provider import RuntimeProvider
from features.external_tools import ExternalTools
from features.game_runner import GameRunner
from features.human_readable_links import HumanReadableLinks
from features.link_user_folders import LinkUserFolders
from features.prefix_selection import PrefixSelection
from features.proton_selection import ProtonSelection
from features.read_config import ReadConfig
from features.sdl_config import SdlConfig
from features.steam_tools import SteamTools
from features.trainer_launch_settings import TrainerLaunchSettings
from features.wine_config import WineConfig
from features.winetricks_install import WinetricksInstall
from gui.main_form import MainForm


class MainApp:
    """
    Represents the main application for the Tinker-Plus program.

    This class serves as the entry point for the application,
    handling initialization, execution, and other top-level application logic.
    """

    def __init__(self):
        parser = argparse.ArgumentParser(description="Tinker-Plus Application")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        subparsers = parser.add_subparsers(title="Commands", dest="command")
        subparsers.required = True

        # Map subcommand functions to handlers
        command_handlers = {
            "install": self.install_as_steam_compatibility_tool,
            "run": self.handle_run_command,
            "": self.handle_run_command,
        }

        subparsers.add_parser("install", help="Install as Steam compatibility tool")

        run_parser = subparsers.add_parser("run", help="Run a game using Tinker-Plus")
        run_parser.add_argument("--gui", action="store_true", help="Run in GUI mode")
        run_parser.add_argument(
            "--dry", action="store_true", help="Run in DRY mode (no game launch)"
        )
        run_parser.add_argument(
            "--trainer", action="store_true", help="Run with trainer"
        )
        run_parser.add_argument(
            "game_command",
            nargs="+",  # Accepts any number of arguments as a list
            help=(
                "The command to launch the game followed by its parameters"
                " (e.g., executable + arguments)"
            ),
        )

        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)

        self.args = parser.parse_args()
        self.handler = command_handlers.get(self.args.command)

        debug_mode = getattr(self.args, "debug", False)

        # Set Steam Game ID from environment variable if available
        game_id = os.getenv("SteamGameId") or "unknown"

        factory = LogFactory.initialize(
            game_id, logging.DEBUG if debug_mode else logging.INFO, True
        )
        self.logger = factory.get_logger("TinkerPlus")

    def run(self):
        """
        Runs the main application.

        This method initializes the application by logging the start process,
        executing the main game functionality, and logging the completion of the application.
        """
        self.logger.info("Starting Tinker-Plus application...")
        if self.handler:
            self.handler(self.args)
        else:
            self.logger.error("No valid command handler found.")
        self.logger.info("Tinker-Plus application finished.")

    def handle_run_command(self, args):
        """
        Handles the logic for the 'run' command.
        Args:
            args (argparse.Namespace): Parsed command-line arguments.
        """
        use_gui = getattr(args, "gui", False)
        dry_run = getattr(args, "dry", False)
        execute_trainer = getattr(args, "trainer", True)
        game_command = getattr(args, "game_command", [])

        try:
            storage = ConfigStorage()
            runtime = RuntimeProvider(
                game_command,
                dry_run,
                # List of feature providers (Order matters as it affects
                # how the command pipeline is built)
                [
                    ExternalTools(),
                    SteamTools(),
                    ProtonSelection(),
                    SdlConfig(),
                    WineConfig(),
                    PrefixSelection(),
                    LinkUserFolders(storage),
                    TrainerLaunchSettings(),
                    WinetricksInstall(),
                    HumanReadableLinks(),
                    GameRunner(),
                    # ReadConfig has to be the last to ensure default
                    # configs are read first, then overridden by user configs
                    ReadConfig(storage),
                ],
            )
            runtime.build_configuration()
            if runtime.runtime_configuration is None:
                raise RuntimeError("Failed to build runtime configuration.")
            runtime.runtime_configuration.execute_trainers = execute_trainer
            if use_gui:
                main_form = MainForm(runtime)
                main_form.show()
            else:
                runtime.run()

        except RuntimeError as e:
            self.logger.error("An error occurred during runtime execution. %s", e)

    def install_as_steam_compatibility_tool(self, _):
        """
        Prepares the application to be installed as a Steam compatibility tool.

        Note:
            This is a placeholder for future implementation and currently does not
            contain any logic.
        """
        self.logger.info(
            "Creating symbolic link for Tinker-Plus (tplus) in '%s'", TPLUS_BIN_LOCATION
        )
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        tinker_plus_sh_path = os.path.join(current_script_directory, "tinker-plus.sh")

        create_symbolic_link(tinker_plus_sh_path, TPLUS_BIN_LOCATION, self.logger)
        # Check if the compatibility tool directory exists, and remove it if it does.
        compat_path = Path(TPLUS_COMPATIBILITY_TOOL_DIR)
        if compat_path.exists() and compat_path.is_dir():
            self.logger.info(
                "Removing existing compatibility tool directory at '%s'",
                TPLUS_COMPATIBILITY_TOOL_DIR,
            )
            shutil.rmtree(compat_path)

        self.logger.info(
            "Installing as Steam compatibility tool at '%s'",
            compat_path,
        )
        compat_path.mkdir(parents=True, exist_ok=True)
        files_to_copy = {
            "toolmanifest.vdf": "./resources/toolmanifest.vdf",
            "compatibilitytool.vdf": "./resources/compatibilitytool.vdf",
        }
        for target, source in files_to_copy.items():
            target_path = compat_path.joinpath(target)
            # Copy the file
            shutil.copy(source, target_path)
        files_to_link = {
            "tplus": tinker_plus_sh_path,
        }

        for link_name, target in files_to_link.items():
            link_path = compat_path.joinpath(link_name)
            create_symbolic_link(target, str(link_path), self.logger)
        self.logger.info("Installation as Steam compatibility tool completed.")


if __name__ == "__main__":
    app = MainApp()
    app.run()
