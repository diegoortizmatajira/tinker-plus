"""Module for generating GUI components based on runtime features."""

from typing import List

# pylint: disable=import-error
import ttkbootstrap as ttk
from ttkbootstrap.style import DANGER, INFO, PRIMARY, SUCCESS

from core.configuration_property import ConfigurationProperty
from core.feature_provider import FeatureAction
from core.log_storage import LogFactory
from core.runtime_provider import RuntimeProvider


class PropertyWrapper:
    """
    A wrapper class for ConfigurationProperty to facilitate GUI generation.

    Attributes:
        property (ConfigurationProperty): The configuration property to be wrapped.
    """

    map = {
        True: "1",
        False: "0",
        None: "",
    }

    def __init__(self, config_property: ConfigurationProperty):
        self.config_property = config_property
        self.variable = ttk.Variable()

    def recover_value(self, configuration: dict):
        """Recovers the value from the GUI variable."""
        value = self.variable.get()
        if self.config_property.type_ref is bool:
            reverse_map = {v: k for k, v in self.map.items()}
            mapped_value = reverse_map.get(value)
        elif self.config_property.type_ref is list and isinstance(value, str):
            mapped_value = value.split(",") if value != "" else []
        else:
            mapped_value = value if value != "" else None

        self.config_property.set(configuration, mapped_value)

    def set_value(self, configuration: dict):
        """Sets the GUI variable from the configuration property."""
        value = self.config_property.get(configuration)
        if self.config_property.type_ref is bool:
            mapped_value = self.map.get(value, value)
        elif self.config_property.type_ref is list and isinstance(value, list):
            mapped_value = ",".join(str(item) for item in value)
        else:
            mapped_value = value if value is not None else ""
        self.variable.set(mapped_value)


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
        self.logger = LogFactory.singleton().get_logger(self.__class__.__name__)

    def __add_wrapper(self, config_property: ConfigurationProperty) -> ttk.Variable:
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

    def __create_action(self, action: FeatureAction):
        # Creates a closure for a feature action to collect the current
        # selected configuration and execute the action.
        def new_action():
            self.recover_values(self.runtime_provider.configuration)
            action.action(
                self.runtime_provider.configuration,
                self.runtime_provider.runtime_configuration,
            )

        return new_action

    def generate_tabs(self, notebook: ttk.Notebook):
        """
        Creates and adds tabs to the provided notebook widget.

        Each tab is generated based on categorized runtime configuration
        properties and their respective features. The method uses categorized
        property data to create corresponding tabs and populates them with
        GUI components.

        Args:
            notebook (Notebook): The notebook widget where tabs will be added.
        """
        self.property_wrappers.clear()
        properties = self.__get_categorized_properties()
        for tab_name, categories in properties.items():
            new_tab = ttk.Frame(notebook)
            notebook.add(new_tab, text=tab_name)
            self.generate_tab_content(new_tab, categories)
        # Generate the actions tab
        actions_tab = ttk.Frame(notebook)
        notebook.add(actions_tab, text="Actions")

        for feature in self.runtime_provider.features:
            if feature.actions and len(feature.actions) > 0:
                feature_frame = ttk.Labelframe(actions_tab, text=feature.name)
                feature_frame.pack(fill="x", padx=5, pady=5)
                for feature_action in feature.actions:
                    ttk.Button(
                        feature_frame,
                        text=feature_action.name,
                        command=self.__create_action(feature_action),
                        bootstyle=INFO,
                    ).pack(side="left", padx=5, pady=5)

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
            category_frame = ttk.Labelframe(tab, text=category_name)
            category_frame.pack(fill="both", expand=True, padx=10, pady=10)
            category_frame.grid_columnconfigure(0, minsize=350)
            category_frame.grid_columnconfigure(1, weight=1)
            row = 0
            for prop in props:
                # Create a variable wrapper for the property
                prop_var = self.__add_wrapper(prop)
                # Create a label for the property
                ttk.Label(category_frame, text=prop.display_name).grid(
                    row=row, column=0, sticky="e", padx=5, pady=5
                )

                # Depending on the property type, create appropriate input widgets
                if prop.type_ref is bool:
                    radio_frame = ttk.Frame(category_frame)
                    radio_frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                    # Create tree radio buttons for: True, False, None
                    ttk.Radiobutton(
                        radio_frame,
                        text="Enabled",
                        variable=prop_var,
                        value="1",
                        bootstyle=SUCCESS,
                    ).pack(side="left", padx=5)
                    ttk.Radiobutton(
                        radio_frame,
                        text="Disabled",
                        variable=prop_var,
                        value="0",
                        bootstyle=DANGER,
                    ).pack(side="left", padx=5)
                    ttk.Radiobutton(
                        radio_frame,
                        text="Default",
                        variable=prop_var,
                        value="",
                        bootstyle=PRIMARY,
                    ).pack(side="left", padx=5)
                elif prop.type_ref is str:
                    if prop.values_provider:
                        # Create a dropdown if there are predefined values
                        ttk.Combobox(
                            category_frame,
                            values=[
                                item.value or item.name
                                for item in prop.get_possible_values(
                                    self.runtime_provider.runtime_configuration,
                                    self.logger,
                                )
                                or []
                            ],
                            textvariable=prop_var,
                        ).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
                    else:
                        # Create a text entry for string properties
                        ttk.Entry(category_frame, textvariable=prop_var).grid(
                            row=row, column=1, sticky="ew", padx=5, pady=5
                        )
                elif prop.type_ref is list:
                    ttk.Entry(category_frame, textvariable=prop_var).grid(
                        row=row, column=1, sticky="ew", padx=5, pady=5
                    )
                row += 1

    def display_values(self, configuration: dict):
        """Sets the GUI variables from the configuration properties."""
        for wrapper in self.property_wrappers:
            wrapper.set_value(configuration)

    def recover_values(self, configuration: dict):
        """Recovers the values from the GUI variables to the configuration properties."""
        for wrapper in self.property_wrappers:
            wrapper.recover_value(configuration)
