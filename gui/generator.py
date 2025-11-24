"""Module for generating GUI components based on runtime features."""

from tkinter import ttk
from tkinter.ttk import Notebook
from core.runtime_provider import RuntimeProvider


class Generator:
    def __init__(self, runtime_provider: RuntimeProvider):
        if not runtime_provider.runtime_configuration:
            raise ValueError("Runtime configuration is required")
        self.runtime_provider = runtime_provider

    def generate(self, notebook: Notebook):
        for feature in self.runtime_provider.features:
            new_tab = ttk.Frame(notebook)
            notebook.add(new_tab, text=feature.__class__.__name__)
