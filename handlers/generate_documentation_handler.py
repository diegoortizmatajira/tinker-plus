"""Handler for generating documentation for Tinker-Plus configuration values."""

import logging
from typing import Any, override

from jinja2 import Environment, FileSystemLoader

from model import AcceptedPropertyTypes
from handlers.base_handler import BaseHandler

GENERATE_DOCUMENTATION_COMMAND = "generate_documentation"


class GenerateDocumentationHandler(BaseHandler):
    """
    Handler for generating documentation for Tinker-Plus configuration values.

    This handler processes configuration properties from all registered features
    and generates a markdown documentation file using a Jinja2 template.

    Attributes:
        Inherits all attributes from BaseHandler.
    """

    def __init__(
        self,
        subparser: Any,  # pyright: ignore[reportExplicitAny, reportAny]
        handlers: dict[str, BaseHandler],
    ) -> None:
        handlers[GENERATE_DOCUMENTATION_COMMAND] = self

        subparser.add_parser(  # pyright: ignore[reportAny]
            GENERATE_DOCUMENTATION_COMMAND,
            help="Generate documentation for Tinker-Plus configuration values",
        )

    @override
    def handle(
        self,
        _args: object,
        logger: logging.Logger,
    ) -> None:
        """
        Generates documentation for the Tinker-Plus application.

        Note:
            This is a placeholder for future implementation and currently does not
            contain any logic.
        """
        logger.info("Generating documentation... (not yet implemented)")
        runtime = self.get_runtime_provider([], True)
        properties: list[dict[str, AcceptedPropertyTypes | None]] = []
        for feature in runtime.features:
            for prop in feature.properties:
                properties.append(
                    {
                        "name": prop.name,
                        "type_ref": prop.type_ref.__name__,
                        "description": prop.description,
                        "default": prop.default,
                    }
                )
        properties.sort(key=lambda x: str(x["name"]))
        # Load templates from current directory
        env = Environment(loader=FileSystemLoader("./resources/"))

        # Load the template file
        template = env.get_template("configuration_reference_template.md")

        # Render with object/dictionary
        output_text = template.render(properties=properties)

        # Save to a text file
        with open("configuration_reference.md", "w", encoding="utf-8") as f:
            _ = f.write(output_text)
        logger.info("Documentation generated: configuration_reference.md")
