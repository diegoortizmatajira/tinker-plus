"""Main Form with Tabs GUI Module"""

import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Progressbar

from core import RuntimeProvider
from gui.generator import Generator


class MainForm:
    def __init__(self, runtime_provider: RuntimeProvider):
        if not runtime_provider.runtime_configuration:
            raise ValueError("Runtime configuration is required")
        self.generator = Generator(runtime_provider)
        self.form = tk.Tk()
        self.form.title("Main Form with Tabs")
        self.form.geometry("500x500")
        # Create the main Notebook (tabbed control)
        self.notebook = ttk.Notebook(self.form)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create the first tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main Tab")

        # Add an image placeholder to the tab
        self.image_label = tk.Label(
            self.main_tab, text="[Image Placeholder]", width=40, height=20, bg="grey"
        )
        self.image_label.pack(pady=10)

        # Add a progress bar
        self.progress_bar = Progressbar(
            self.main_tab, orient="horizontal", length=300, mode="determinate"
        )
        self.progress_bar.pack(pady=10)

        # Add Play buttons
        self.play_with_trainer_button = tk.Button(
            self.main_tab,
            text="Play with Trainer",
            command=self.on_play_with_trainer_click,
        )
        self.play_with_trainer_button.pack(side="left", padx=5, pady=10)

        self.just_play_button = tk.Button(
            self.main_tab, text="Just Play", command=self.on_just_play_click
        )
        self.just_play_button.pack(side="right", padx=5, pady=10)

        self.generator.generate_tabs(self.notebook)

        # Binding
        self.runtime_provider = runtime_provider

        # temp_has_trainers = runtime_provider.runtime_configuration.has_trainers
        # self.just_play_button.configure(
        #     default=temp_has_trainers and tk.NORMAL or tk.ACTIVE
        # )
        # self.play_with_trainer_button.configure(
        #     state=temp_has_trainers and tk.NORMAL or tk.DISABLED,
        #     default=temp_has_trainers and tk.ACTIVE or tk.NORMAL,
        # )

    def on_play_with_trainer_click(self):
        # Default handler for Play with Trainer button
        print("Play with Trainer clicked")
        self.runtime_provider.run(True)

    def on_just_play_click(self):
        # Default handler for Just Play button
        print("Just Play clicked")
        self.runtime_provider.run(False)

    def show(self):
        self.form.mainloop()
