"""Module for generating GUI components based on runtime features."""

import tkinter as tk

from tkinter import ttk
from tkinter.ttk import Notebook
from typing import List
from core.configuration_property import ConfigurationProperty
from core.runtime_provider import RuntimeProvider


class Generator:
    def __init__(self, runtime_provider: RuntimeProvider):
        if not runtime_provider.runtime_configuration:
            raise ValueError("Runtime configuration is required")
        self.runtime_provider = runtime_provider

    def __get_categorized_properties(
        self,
    ) -> dict[str, dict[str, List[ConfigurationProperty]]]:
        categorized_properties = {}
        for feature in self.runtime_provider.features:
            tab = categorized_properties.get(feature.category, {})
            category = tab.get(feature.name, [])
            category.extend(feature.properties)
            if len(category) > 0:
                tab[feature.name] = category
            if len(tab) > 0:
                categorized_properties[feature.category] = tab

        return categorized_properties

    def generate_tabs(self, notebook: Notebook):
        properties = self.__get_categorized_properties()
        for tab_name, categories in properties.items():
            new_tab = ttk.Frame(notebook)
            notebook.add(new_tab, text=tab_name)
            self.generate_tab_content(new_tab, categories)

    def generate_tab_content(
        self, tab: ttk.Frame, categories: dict[str, List[ConfigurationProperty]]
    ):
        for category_name, props in categories.items():
            # Create a labeled frame for each category
            category_frame = ttk.LabelFrame(tab, text=category_name)
            category_frame.pack(fill="both", expand=True, padx=10, pady=10)
            for prop in props:
                # Depending on the property type, create appropriate input widgets
                if prop.type_ref is bool:
                    # Create a checkbox for boolean properties
                    prop_var = tk.BooleanVar()
                    prop_check = ttk.Checkbutton(
                        category_frame, variable=prop_var, text=prop.name
                    )
                    prop_check.pack(anchor="w", padx=5, pady=2)
                elif prop.type_ref is str:
                    prop_label = ttk.Label(category_frame, text=prop.name)
                    prop_label.pack(anchor="w", padx=5, pady=2)
                    if prop.values_provider:
                        # Create a dropdown if there are predefined values
                        prop_combo = ttk.Combobox(
                            category_frame,
                            values=[
                                item.value or item.name
                                for item in prop.get_possible_values(
                                    self.runtime_provider.runtime_configuration
                                )
                                or []
                            ],
                        )
                        prop_combo.pack(fill="x", padx=5, pady=2)
                    else:
                        # Create a text entry for string properties
                        prop_entry = ttk.Entry(category_frame)
                        prop_entry.pack(fill="x", padx=5, pady=2)
                elif prop.type_ref is list:
                    prop_label = ttk.Label(category_frame, text=prop.name)
                    prop_label.pack(anchor="w", padx=5, pady=2)
                    prop_entry = ttk.Entry(category_frame)
                    prop_entry.pack(fill="x", padx=5, pady=2)
