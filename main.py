"""
Main entry point for the Tinker-Plus application.
"""

import logging
import os
import sys
import argparse
from core.runtime_provider import RuntimeProvider
from features.game_runner import GameRunner
from features.link_user_folders import LinkUserFolders
from features.prefix_selection import PrefixSelection
from features.proton_selection import ProtonSelection
from features.read_config import ReadConfig
from features.steam_context_reader import SteamContextReader
from features.trainer_launch_settings import TrainerLaunchSettings
from gui.main_form import MainForm


class MainApp:
    """
    Represents the main application for the Tinker-Plus program.

    This class serves as the entry point for the application,
    handling initialization, execution, and other top-level application logic.
    """

    def __init__(self):
        self.logger = logging.getLogger("tinker-plus")

    def run(self):
        """
        Runs the main application.

        This method initializes the application by logging the start process,
        executing the main game functionality, and logging the completion of the application.
        """
        parser = argparse.ArgumentParser(description="Tinker-Plus Application")
        subparsers = parser.add_subparsers(dest="command")

        # Install command
        subparsers.add_parser("install", help="Install as Steam compatibility tool")

        # Run command
        run_parser = subparsers.add_parser("run", help="Run a game using Tinker-Plus")
        run_parser.add_argument("cli", action="store_true", help="Run in CLI-only mode")

        # Parse args
        args = parser.parse_args()

        # Default to "run" if no command is provided
        self.logger.info("Starting Tinker-Plus application...")
        if args.command == "install":
            self.install_as_steam_compatibility_tool()
        else:
            # args.command is "run" or None
            use_cli = getattr(args, "cli", False)
            self.execute_game(not use_cli)
        self.logger.info("Tinker-Plus application finished.")

    def install_as_steam_compatibility_tool(self):
        """
        Prepares the application to be installed as a Steam compatibility tool.

        Note:
            This is a placeholder for future implementation and currently does not
            contain any logic.
        """
        # Placeholder for future implementation

    # def save_environment_variables(self):
    #     """
    #     Saves the current environment variables to a persistent storage.
    #
    #     Note:
    #         This is a placeholder for future implementation and currently does not
    #         contain any logic.
    #     """
    #     output_file = "/home/diegoortizmatajira/environment_variables.txt"
    #     # Read all environment variables and save them to output_file
    #     with open(output_file, "a", encoding="utf-8") as f:
    #         for var, value in os.environ.items():
    #             f.write(f"{var}={value}\n")
    #         # Also write a separator for clarity
    #         f.write("\n--- End of Environment Variables ---\n\n")
    #         # Also write any parameters passed to the application
    #         f.write("Application Parameters:\n")
    #         for param in sys.argv:
    #             f.write(f"{param}\n")

    def execute_game(self, use_ui: bool = True):
        """
        Executes the game with the given runtime configuration.

        Args:
            use_ui (bool): Determines whether to use the graphical UI for the game execution.
                           If set to True, the MainForm UI is displayed; otherwise, the game
                           is executed directly in the runtime without a UI.
        """
        # self.save_environment_variables()
        try:
            runtime = RuntimeProvider(
                [
                    SteamContextReader(),
                    ReadConfig(),
                    ProtonSelection(),
                    PrefixSelection(),
                    LinkUserFolders(),
                    TrainerLaunchSettings(),
                    GameRunner(),
                ]
            )
            runtime.build_configuration()
            if use_ui:
                main_form = MainForm(runtime)
                main_form.show()
            else:
                runtime.run()

        except RuntimeError as e:
            self.logger.error("An error occurred during runtime execution. %s", e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = MainApp()
    app.run()
