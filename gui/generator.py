"""Module for generating GUI components based on runtime features."""

import tkinter as tk

from tkinter import Variable, ttk
from tkinter.ttk import Notebook
from typing import List
from core.configuration_property import ConfigurationProperty
from core.runtime_provider import RuntimeProvider


class PropertyWrapper:
    """
    A wrapper class for ConfigurationProperty to facilitate GUI generation.

    Attributes:
        property (ConfigurationProperty): The configuration property to be wrapped.
    """

    def __init__(self, config_property: ConfigurationProperty):
        self.config_property = config_property
        self.variable = tk.Variable()

    def recover_value(self, configuration: dict):
        """Recovers the value from the GUI variable."""
        self.config_property.set(configuration, self.variable.get())

    def set_value(self, configuration: dict):
        """Sets the GUI variable from the configuration property."""
        value = self.config_property.get(configuration)
        if value is not None:
            self.variable.set(value)


class Generator:
    """
    A class responsible for generating GUI components based on runtime features.

    Attributes:
        runtime_provider (RuntimeProvider): Provides the runtime configuration
        and features for categorization.

    Methods:
        __get_categorized_properties() -> dict[str, dict[str, List[ConfigurationProperty]]]:
            Categorizes properties based on their features and returns a nested dictionary.

        generate_tabs(notebook: Notebook):
            Creates tabs within a notebook widget based on categorized properties.

        generate_tab_content(tab: ttk.Frame, categories: dict[str, List[ConfigurationProperty]]):
            Populates a given tab with categorized properties and the corresponding GUI components.
    """

    def __init__(self, runtime_provider: RuntimeProvider):
        if not runtime_provider.runtime_configuration:
            raise ValueError("Runtime configuration is required")
        self.runtime_provider = runtime_provider
        self.property_wrappers: List[PropertyWrapper] = []

    def __add_wrapper(self, config_property: ConfigurationProperty) -> Variable:
        wrapper = PropertyWrapper(config_property)
        self.property_wrappers.append(wrapper)
        return wrapper.variable

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
        """
        Creates and adds tabs to the provided notebook widget.

        Each tab is generated based on categorized runtime configuration
        properties and their respective features. The method uses categorized
        property data to create corresponding tabs and populates them with
        GUI components.

        Args:
            notebook (Notebook): The notebook widget where tabs will be added.
        """
        properties = self.__get_categorized_properties()
        for tab_name, categories in properties.items():
            new_tab = ttk.Frame(notebook)
            notebook.add(new_tab, text=tab_name)
            self.generate_tab_content(new_tab, categories)

    def generate_tab_content(
        self, tab: ttk.Frame, categories: dict[str, List[ConfigurationProperty]]
    ):
        """
        Populates the given tab with categorized configuration properties.

        This method creates a labeled frame for each category within the `categories`
        dictionary and populates it with appropriate input widgets based on the
        properties' types. Supported property types include boolean, string, and list.

        Args:
            - tab (ttk.Frame): The tab frame where the categorized properties will be added.
            - categories (dict[str, List[ConfigurationProperty]]): A dictionary where keys
            represent category names and values are the list of configuration properties
            for each category.
        """
        for category_name, props in categories.items():
            # Create a labeled frame for each category
            category_frame = ttk.LabelFrame(tab, text=category_name)
            category_frame.pack(fill="both", expand=True, padx=10, pady=10)
            for prop in props:
                # Depending on the property type, create appropriate input widgets
                if prop.type_ref is bool:
                    # Create a checkbox for boolean properties
                    prop_var = self.__add_wrapper(prop)
                    # prop_label = ttk.Label(category_frame, text=prop.display_name)
                    # prop_label.pack(anchor="w", padx=5, pady=2)
                    chk = tk.Checkbutton(
                        category_frame,
                        text=prop.display_name,
                        variable=prop_var,
                        onvalue=True,  # Checked
                        offvalue=False,  # Unchecked
                        tristatevalue=None,  # Indeterminate (null)
                    )
                    chk.pack(anchor="w", padx=5, pady=5)
                    # # Insert a container for radio buttons to be horizontally aligned
                    # radio_container = ttk.Frame(category_frame)
                    # radio_container.pack(anchor="w", padx=5, pady=2)
                    # # Create radio buttons
                    # rb_default = tk.Radiobutton(
                    #     radio_container, text="Default", variable=prop_var, value="None"
                    # )
                    # rb_true = tk.Radiobutton(
                    #     radio_container, text="True", variable=prop_var, value="True"
                    # )
                    # rb_false = tk.Radiobutton(
                    #     radio_container, text="False", variable=prop_var, value="False"
                    # )
                    #
                    # # Pack them
                    # rb_default.pack(side="left", padx=3)
                    # rb_true.pack(side="left", padx=3)
                    # rb_false.pack(side="left", padx=3)
                elif prop.type_ref is str:
                    prop_label = ttk.Label(category_frame, text=prop.display_name)
                    prop_label.pack(anchor="w", padx=5, pady=2)
                    if prop.values_provider:
                        prop_var = self.__add_wrapper(prop)
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
                            textvariable=prop_var,
                        )
                        prop_combo.pack(fill="x", padx=5, pady=5)
                    else:
                        prop_var = self.__add_wrapper(prop)
                        # Create a text entry for string properties
                        prop_entry = ttk.Entry(category_frame, textvariable=prop_var)
                        prop_entry.pack(fill="x", padx=5, pady=5)
                elif prop.type_ref is list:
                    prop_label = ttk.Label(category_frame, text=prop.display_name)
                    prop_label.pack(anchor="w", padx=5, pady=2)
                    prop_var = self.__add_wrapper(prop)
                    prop_entry = ttk.Entry(category_frame, textvariable=prop_var)
                    prop_entry.pack(fill="x", padx=5, pady=5)

    def display_values(self, configuration: dict):
        """Sets the GUI variables from the configuration properties."""
        for wrapper in self.property_wrappers:
            wrapper.set_value(configuration)

    def recover_values(self, configuration: dict):
        """Recovers the values from the GUI variables to the configuration properties."""
        for wrapper in self.property_wrappers:
            wrapper.recover_value(configuration)
