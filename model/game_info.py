"""Module for managing game information and caching."""

from dataclasses import dataclass


@dataclass
class GameInfo:
    """
    Represents information about a game, including its unique identifier
    and name. This class also provides methods for managing and accessing
    a cache of game information.

    Attributes:
        game_id (str): The unique identifier for the game.
        name (str): The name of the game.
    """

    game_id: str
    name: str

    @staticmethod
    def empty() -> "GameInfo":
        """
        Creates an empty GameInfo object with default values.

        Returns:
            GameInfo: An empty GameInfo object with default values.
        """
        return GameInfo(game_id="unknown", name="unknown")
