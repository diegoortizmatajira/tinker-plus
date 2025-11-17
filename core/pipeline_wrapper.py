"""Module defining the PipelineWrapper dataclass for wrapping pipeline commands."""

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass()
class PipelineWrapper:
    """
    Represents a pipeline wrapper with environment variables and a command to execute.
    Attributes:
        environment_variables (dict[str, str]): A dictionary of environment variables to set.
        command (str): The command to execute within the pipeline wrapper.
    """

    command: str
    wrapper: Optional[Callable[[str], str]] = None

    def wrap(self, pipeline_assembled_command: str) -> str:
        """
        Wraps the provided pipeline assembled command using the defined wrapper.

        If a wrapper is defined, it applies the wrapper function to the pipeline
        assembled command. Otherwise, it concatenates the command and the pipeline
        assembled command.

        Args:
            pipeline_assembled_command (str): The assembled command to be wrapped.

        Returns:
            str: The wrapped command.
        """
        if self.wrapper:
            wrapped_command = self.wrapper(pipeline_assembled_command)
            return wrapped_command
        wrapped_command = f"{self.command} {pipeline_assembled_command}"
        return wrapped_command
