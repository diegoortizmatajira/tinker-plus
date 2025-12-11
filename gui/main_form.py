"""Main Form with Tabs GUI Module"""

from tkinter import Event, Widget
import tkinter.font as tkfont
from typing import final
import webbrowser
from pathlib import Path

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.style import (
    DANGER,
    DEFAULT,
    INFO,
    OUTLINE,
    PRIMARY,
    SECONDARY,
    STRIPED,
    SUCCESS,
)

from core import RuntimeProvider
from core.defaults import (
    LOG_TIMER_ACTION,
    LOG_USER_ACTION,
)
from core.log_storage import LogFactory
from core.steam import get_steam_header_image_path
from gui.generator import Generator


# pylint: disable=too-many-instance-attributes
@final
class MainForm:
    """
    The MainForm class represents the primary graphical user interface (GUI) component
    with tabbed functionality. It manages the main application window, including tabs,
    buttons, and other UI elements.

    Attributes:
        generator (Generator): The generator instance responsible for creating tabs.
        form (tk.Tk): The main application window.
        notebook (ttk.Notebook): A tabbed notebook control.
        main_tab (ttk.Frame): The first tab of the notebook.
        image_label (tk.Label): A placeholder label for an image display.
        progress_bar (Progressbar): A progress bar in the main tab.
        play_with_trainer_button (tk.Button): A button to initiate "Play with Trainer" mode.
        just_play_button (tk.Button): A button to initiate "Just Play" mode.
        runtime_provider (RuntimeProvider): Provides runtime configuration for the application.

    Methods:
        __init__(runtime_provider: RuntimeProvider):
            Initializes the MainForm, validates the runtime configuration, and sets up the GUI.
        on_play_with_trainer_click():
            Handles the "Play with Trainer" button click event, invoking the runtime with trainers.
        on_just_play_click():
            Handles the "Just Play" button click event, invoking the runtime without trainers.
        show():
            Displays the main application window and starts the Tkinter main event loop.
    """

    def __init__(
        self, runtime_provider: RuntimeProvider, countdown_in_seconds: int = 3
    ):
        self.logger = LogFactory.singleton().get_logger(self.__class__.__name__)
        if not runtime_provider.runtime_configuration:
            self.logger.error("Runtime configuration is required")
            raise ValueError("Runtime configuration is required")
        self.runtime_provider = runtime_provider
        self.logger.info("Initializing application main form")
        self.countdown_in_seconds = countdown_in_seconds
        self.remaining_seconds = countdown_in_seconds
        self.timer_running = False
        self.generator = Generator(runtime_provider)
        self.form = ttk.Window(
            f"Tinker-Plus: {runtime_provider.runtime_configuration.game_info.name}",
            themename="superhero",
        )
        self.form.geometry("1024x768")
        self.form.minsize(1024, 768)
        # Create the main Notebook (tabbed control)
        self.default_font = tkfont.nametofont("TkDefaultFont")
        self.game_image: ImageTk.PhotoImage | None = None
        self.notebook = ttk.Notebook(self.form)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        self.__generate_main_tab()
        self.generator.generate_tabs(self.notebook)

        # Create a frame for buttons at the bottom
        button_frame = ttk.Frame(self.form)
        button_frame.pack(fill="x", pady=5)

        # Add a progress bar
        self.progress_bar = ttk.Progressbar(
            button_frame,
            orient="horizontal",
            value=self.remaining_seconds,
            maximum=self.countdown_in_seconds,
            mode="determinate",
            bootstyle=STRIPED,
        )
        self.progress_bar.pack(padx=5, pady=2, fill="x")

        # Add Play buttons
        ttk.Button(
            button_frame,
            text="Just Play",
            command=self.on_just_play_click,
            bootstyle=SUCCESS,
        ).pack(side="right", padx=5, pady=5)
        ttk.Button(
            button_frame,
            text="Play with Trainer",
            command=self.on_play_with_trainer_click,
            bootstyle=PRIMARY,
            style=(DEFAULT),
        ).pack(side="right", padx=5, pady=5)
        ttk.Button(
            button_frame,
            text="Save Config",
            command=self.on_save_config_click,
            bootstyle=(INFO, OUTLINE),
        ).pack(side="left", padx=5, pady=5)
        ttk.Button(
            button_frame,
            text="Close",
            command=self.on_close_click,
            bootstyle=(DANGER, OUTLINE),
        ).pack(side="left", padx=5, pady=5)
        # Bind all mouse and keyboard events to root
        _ = self.form.bind_all("<Button>", self.on_user_interaction)  # any mouse click
        _ = self.form.bind_all("<Key>", self.on_user_interaction)  # any key press
        # Binding
        self.generator.display_values(self.runtime_provider.configuration)

    def __display_property(
        self,
        root: Widget,
        property_name: str,
        property_value: str | None,
        link_text: str | None = None,
    ):
        frame = ttk.Frame(root)
        frame.pack(fill="x", pady=2, padx=5)
        bold_font = self.default_font.copy()
        _ = bold_font.configure(weight=tkfont.BOLD)
        ttk.Label(
            frame,
            text=f"{property_name}:",
            font=bold_font,
            anchor="w",
        ).pack(side="left", padx=3)
        # Display as normal text with wrapping
        value_label = ttk.Label(
            frame,
            text=property_value or "",
            anchor="w",
            wraplength=500,
        )
        value_label.pack(side="left", padx=3)
        if link_text:
            # Make it look like a hyperlink
            underlined_font = self.default_font.copy()
            _ = underlined_font.configure(underline=True)
            value_label.configure(
                text=link_text,
                font=underlined_font,
                cursor="hand2",
                anchor="w",
                bootstyle=INFO,
            )
            _ = value_label.bind(
                "<Button-1>",
                lambda _: webbrowser.open_new(property_value or ""),
            )

    def __generate_main_tab(self):
        # Create the first tab
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="Main Tab")
        title_font = self.default_font.copy()
        _ = title_font.configure(size=16, weight=tkfont.BOLD)
        ttk.Label(
            main_tab,
            text=self.runtime_provider.runtime_configuration.game_info.name,
            font=title_font,
        ).pack(pady=10)

        img_path = get_steam_header_image_path(
            self.runtime_provider.runtime_configuration
        )
        if img_path:
            self.logger.debug("Loading header image from '%s'", img_path)
            # Add an image placeholder to the tab
            img = Image.open(img_path)
            self.game_image = ImageTk.PhotoImage(img)
            # Create a label to hold the image
            image_label = ttk.Label(
                main_tab, image=self.game_image, text="Header Image"
            )
            image_label.pack(pady=5)
        else:
            self.logger.warning("There is no header image")

        game_name_for_search = (
            self.runtime_provider.runtime_configuration.game_info.name.replace(" ", "+")
        )
        game_id = self.runtime_provider.runtime_configuration.steam_game_id
        self.__display_property(
            main_tab,
            "Game Id",
            game_id,
        )
        relative_exe_path = Path(
            self.runtime_provider.runtime_configuration.steam_game_exe or ""
        ).relative_to(
            self.runtime_provider.runtime_configuration.steam_compat_install_path or "/"
        )
        self.__display_property(
            main_tab,
            "Game Executable",
            relative_exe_path.as_posix(),
        )
        self.__display_property(
            main_tab,
            "Technical Info",
            f"https://steamdb.info/app/{game_id}/",
            link_text="View on Steam DB",
        )
        self.__display_property(
            main_tab,
            "Game Compatibility Reports",
            f"https://www.protondb.com/app/{game_id}",
            link_text="View on ProtonDB",
        )
        self.__display_property(
            main_tab,
            "Game Info & Fixes",
            f"https://www.pcgamingwiki.com/w/index.php?search={game_name_for_search}",
            link_text="View on PCGamingWiki",
        )
        self.__display_property(
            main_tab,
            "Trainers & Mods",
            f"https://flingtrainer.com/?s={game_name_for_search}",
            link_text="Search on Fling Trainer",
        )

    def on_user_interaction(self, _event: Event) -> object:
        """
        Handles user interaction events such as mouse clicks or key presses.

        This method stops the countdown timer whenever a user interaction is detected,
        ensuring that the application avoids initiating actions during active user activity.

        Args:
            event (Event): The event object generated by the user interaction.
        """
        if self.timer_running:
            self.logger.info(
                LOG_USER_ACTION.format(
                    "User interaction detected, stopping timer for auto-play."
                )
            )
            self.timer_running = False
            self.progress_bar["value"] = self.countdown_in_seconds
            self.progress_bar.configure(bootstyle=(SECONDARY, STRIPED))

    def on_timer_tick(self):
        """
        Handles the timer tick event for countdown progress.

        This method decreases the remaining countdown seconds, updates the progress bar,
        and schedules the next tick. When the countdown reaches zero, it stops the timer
        and starts the game.
        """
        if self.timer_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.progress_bar["value"] = self.remaining_seconds
            _ = self.form.after(1000, self.on_timer_tick)
        elif self.timer_running and self.remaining_seconds == 0:
            self.logger.info(
                LOG_TIMER_ACTION.format("Countdown finished, game will start now")
            )
            self.timer_running = False
            self.__play(with_trainers=True)

    def on_save_config_click(self, _event: Event) -> object:
        """
        Handles the click event for the "Save Config" button.

        This method saves the current configuration values from the GUI
        back to the runtime provider's configuration.
        """
        self.logger.info("Saving configuration from GUI to runtime provider")
        self.generator.recover_values(self.runtime_provider.configuration)
        self.runtime_provider.config_storage.save_game_config(
            self.runtime_provider.configuration,
            self.runtime_provider.runtime_configuration.steam_game_id,
            self.runtime_provider.runtime_configuration.loaded_global_configuration,
        )

    def __play(self, with_trainers: bool):
        self.logger.info("Starting play mode, with_trainers=%s", with_trainers)
        self.generator.recover_values(self.runtime_provider.configuration)
        self.form.destroy()
        self.runtime_provider.run(with_trainers)

    def on_play_with_trainer_click(self, _event: Event) -> object:
        """
        Handles the click event for the "Play with Trainer" button.

        This method initiates the runtime in the "Play with Trainer" mode,
        ensuring that the application operates with trainers enabled.
        """
        self.logger.info(LOG_USER_ACTION.format("Play with Trainer clicked"))
        self.__play(True)

    def on_just_play_click(self, _event: Event) -> object:
        """
        Handles the click event for the "Just Play" button.

        This method initiates the runtime in the "Just Play" mode,
        ensuring that the application operates without trainers enabled.
        """
        self.logger.info(LOG_USER_ACTION.format("Just Play clicked"))
        self.__play(False)

    def on_close_click(self, _event: Event) -> object:
        """
        Handles the click event for the "Close" button.

        This method closes the main application window and exits the program.
        """
        self.logger.info(LOG_USER_ACTION.format("Close clicked, exiting application"))
        self.form.destroy()

    def show(self):
        """
        Displays the main application window and starts the Tkinter main event loop.

        This method is responsible for launching the graphical user interface (GUI)
        and entering the main event loop of the Tkinter library to handle user interactions.
        """
        # Activates timer
        self.logger.info(
            LOG_TIMER_ACTION.format("Starting countdown timer for auto-play")
        )
        # Only start timer if countdown is greater than 0
        if self.countdown_in_seconds > 0:
            self.timer_running = True
            self.on_timer_tick()
        # Start the Tkinter main event loop
        self.form.mainloop()
