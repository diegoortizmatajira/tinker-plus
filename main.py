"""
Main entry point for the Tinker-Plus application.
"""

import sys
import argparse
from core import logger_factory
from core.config_storage import ConfigStorage
from core.runtime_provider import RuntimeProvider
from features.game_runner import GameRunner
from features.link_user_folders import LinkUserFolders
from features.prefix_selection import PrefixSelection
from features.proton_selection import ProtonSelection
from features.read_config import ReadConfig
from features.trainer_launch_settings import TrainerLaunchSettings
from features.winetricks_install import WinetricksInstall
from gui.main_form import MainForm


class MainApp:
    """
    Represents the main application for the Tinker-Plus program.

    This class serves as the entry point for the application,
    handling initialization, execution, and other top-level application logic.
    """

    def __init__(self):
        self.logger = logger_factory.get_logger(self.__class__.__name__)

    def run(self):
        """
        Runs the main application.

        This method initializes the application by logging the start process,
        executing the main game functionality, and logging the completion of the application.
        """
        parser = argparse.ArgumentParser(description="Tinker-Plus Application")

        subparsers = parser.add_subparsers(title="Commands", dest="command")
        subparsers.required = True

        # Map subcommand functions to handlers
        command_handlers = {
            "install": self.install_as_steam_compatibility_tool,
            "run": self.handle_run_command,
        }

        subparsers.add_parser("install", help="Install as Steam compatibility tool")

        run_parser = subparsers.add_parser("run", help="Run a game using Tinker-Plus")
        run_parser.add_argument(
            "--cli", action="store_true", help="Run in CLI-only mode"
        )
        run_parser.add_argument(
            "--dry", action="store_true", help="Run in DRY mode (no game launch)"
        )
        run_parser.add_argument(
            "--trainer", action="store_true", help="Run with trainer"
        )
        run_parser.add_argument(
            "game_command",
            nargs="+",  # Accepts any number of arguments as a list
            help="The command to launch the game followed by its parameters (e.g., executable + arguments)",
        )

        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)

        args = parser.parse_args()

        self.logger.info("Starting Tinker-Plus application...")
        handler = command_handlers.get(args.command)
        if handler:
            handler(args)
        self.logger.info("Tinker-Plus application finished.")

    def handle_run_command(self, args):
        """
        Handles the logic for the 'run' command.
        Args:
            args (argparse.Namespace): Parsed command-line arguments.
        """
        use_cli = getattr(args, "cli", False)
        dry_run = getattr(args, "dry", False)
        execute_trainer = getattr(args, "trainer", True)
        game_command = getattr(args, "game_command", [])

        try:
            storage = ConfigStorage()
            runtime = RuntimeProvider(
                game_command,
                dry_run,
                [
                    ProtonSelection(),
                    PrefixSelection(),
                    LinkUserFolders(),
                    TrainerLaunchSettings(),
                    WinetricksInstall(),
                    # ReadConfig has to be the last before GameRunner, to ensure default
                    # configs are read first, then overridden by user configs
                    ReadConfig(storage),
                    GameRunner(),
                ],
            )
            runtime.build_configuration()
            if runtime.runtime_configuration is None:
                raise RuntimeError("Failed to build runtime configuration.")
            runtime.runtime_configuration.execute_trainers = execute_trainer
            if use_cli:
                runtime.run()
            else:
                main_form = MainForm(runtime)
                main_form.show()

        except RuntimeError as e:
            self.logger.error("An error occurred during runtime execution. %s", e)

    def install_as_steam_compatibility_tool(self, _):
        """
        Prepares the application to be installed as a Steam compatibility tool.

        Note:
            This is a placeholder for future implementation and currently does not
            contain any logic.
        """
        self.logger.info("Installing as Steam compatibility tool... (not implemented)")


if __name__ == "__main__":
    app = MainApp()
    app.run()
