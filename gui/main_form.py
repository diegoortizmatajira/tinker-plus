"""Main Form with Tabs GUI Module"""

# pylint: disable=import-error
import ttkbootstrap as ttk
from ttkbootstrap.style import INFO, OUTLINE, PRIMARY, SECONDARY, STRIPED, SUCCESS

from core import RuntimeProvider
from core.defaults import LOG_TIMER_ACTION, LOG_USER_ACTION
from core.log_storage import LogFactory
from gui.generator import Generator


# pylint: disable=too-many-instance-attributes
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
        self.logger.info("Initializing application main form")
        self.countdown_in_seconds = countdown_in_seconds
        self.remaining_seconds = countdown_in_seconds
        self.timer_running = False
        self.generator = Generator(runtime_provider)
        self.form = ttk.Window()
        self.form.title(
            f"Tinker-Plus: {runtime_provider.runtime_configuration.game_info.name}"
        )
        self.form.geometry("800x600")
        self.form.minsize(800, 600)
        # Create the main Notebook (tabbed control)
        self.notebook = ttk.Notebook(self.form)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Create the first tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main Tab")
        ttk.Label(
            self.main_tab,
            text=runtime_provider.runtime_configuration.game_info.name,
            font=("Arial", 16, "bold"),
        ).pack(pady=10)

        # Add an image placeholder to the tab
        self.image_label = ttk.Label(self.main_tab, text="[Image Placeholder]")
        self.image_label.pack(fill="x", pady=10)


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
            bootstyle=(SECONDARY, OUTLINE),
        ).pack(side="left", padx=5, pady=5)

        self.generator.generate_tabs(self.notebook)
        # Bind all mouse and keyboard events to root
        self.form.bind_all("<Button>", self.on_user_interaction)  # any mouse click
        self.form.bind_all("<Key>", self.on_user_interaction)  # any key press
        # Binding
        self.runtime_provider = runtime_provider
        self.generator.display_values(self.runtime_provider.configuration)

        # temp_has_trainers = runtime_provider.runtime_configuration.has_trainers
        # self.just_play_button.configure(
        #     default=temp_has_trainers and tk.NORMAL or tk.ACTIVE
        # )
        # self.play_with_trainer_button.configure(
        #     state=temp_has_trainers and tk.NORMAL or tk.DISABLED,
        #     default=temp_has_trainers and tk.ACTIVE or tk.NORMAL,
        # )

    def on_user_interaction(self, _):
        """
        Handles user interaction events such as mouse clicks or key presses.

        This method stops the countdown timer whenever a user interaction is detected,
        ensuring that the application avoids initiating actions during active user activity.

        Args:
            event (Event): The event object generated by the user interaction.
        """
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
            self.form.after(1000, self.on_timer_tick)
        elif self.timer_running and self.remaining_seconds == 0:
            self.logger.info(
                LOG_TIMER_ACTION.format("Countdown finished, game will start now")
            )
            self.timer_running = False
            self.__play(with_trainers=True)

    def on_save_config_click(self):
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

    def on_play_with_trainer_click(self):
        """
        Handles the click event for the "Play with Trainer" button.

        This method initiates the runtime in the "Play with Trainer" mode,
        ensuring that the application operates with trainers enabled.
        """
        self.logger.info(LOG_USER_ACTION.format("Play with Trainer clicked"))
        self.__play(True)

    def on_just_play_click(self):
        """
        Handles the click event for the "Just Play" button.

        This method initiates the runtime in the "Just Play" mode,
        ensuring that the application operates without trainers enabled.
        """
        self.logger.info(LOG_USER_ACTION.format("Just Play clicked"))
        self.__play(False)

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
        self.timer_running = True
        self.on_timer_tick()
        # Start the Tkinter main event loop
        self.form.mainloop()
