"""Module for managing compatibility tool information."""

from dataclasses import dataclass


@dataclass
class CompatToolInfo:
    """
    Represents compatibility tool (Proton/GE-Proton) information.

    Caching of instances of this class is handled separately by
    `repositories.CompatToolInfoRepository`.

    Attributes:
        name (str): The name of the compatibility tool.
        dir (str): The directory where the compatibility tool is located.
    """

    name: str
    dir: str

    @staticmethod
    def empty() -> "CompatToolInfo":
        """
        Create and return an empty CompatToolInfo object.

        This static method creates a CompatToolInfo object with default values.
        It is primarily used as a placeholder or default value.

        Returns:
            CompatToolInfo: An instance of CompatToolInfo with "unknown" as the name
            and "." as the directory.
        """
        return CompatToolInfo(name="unknown", dir=".")
