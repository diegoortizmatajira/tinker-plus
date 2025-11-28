"""Main Form with Tabs GUI Module"""

# pylint: disable=import-error
import ttkbootstrap as ttk
from ttkbootstrap.style import STRIPED, SUCCESS, PRIMARY

from core import RuntimeProvider
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

    def __init__(self, runtime_provider: RuntimeProvider):
        if not runtime_provider.runtime_configuration:
            raise ValueError("Runtime configuration is required")
        self.generator = Generator(runtime_provider)
        self.form = ttk.Window()
        self.form.title("Tinker-Plus")
        self.form.geometry("800x600")
        # Create the main Notebook (tabbed control)
        self.notebook = ttk.Notebook(self.form)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Create the first tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main Tab")

        # Add an image placeholder to the tab
        self.image_label = ttk.Label(
            self.main_tab, text="[Image Placeholder]", width=40
        )
        self.image_label.pack(pady=10)

        button_frame = ttk.Frame(self.form).pack(fill="x", pady=5)
        # Add a progress bar
        self.progress_bar = ttk.Progressbar(
            button_frame,
            orient="horizontal",
            value=50,
            length=100,
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

        self.generator.generate_tabs(self.notebook)

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

    def __play(self, with_trainers: bool):
        self.generator.recover_values(self.runtime_provider.configuration)
        self.runtime_provider.run(with_trainers)

    def on_play_with_trainer_click(self):
        """
        Handles the click event for the "Play with Trainer" button.

        This method initiates the runtime in the "Play with Trainer" mode,
        ensuring that the application operates with trainers enabled.
        """
        print("Play with Trainer clicked")
        self.__play(True)

    def on_just_play_click(self):
        """
        Handles the click event for the "Just Play" button.

        This method initiates the runtime in the "Just Play" mode,
        ensuring that the application operates without trainers enabled.
        """
        print("Just Play clicked")
        self.__play(False)

    def show(self):
        """
        Displays the main application window and starts the Tkinter main event loop.

        This method is responsible for launching the graphical user interface (GUI)
        and entering the main event loop of the Tkinter library to handle user interactions.
        """
        self.form.mainloop()
