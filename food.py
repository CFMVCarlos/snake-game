"""Food entity and spawning prototype pattern implementation."""

from __future__ import annotations

import random


class Food:
    """Represents a collectible food item on the game board.

    Parameters
    ----------
    start_width : int
        Minimum horizontal cell coordinate.
    stop_width : int
        Maximum horizontal cell coordinate.
    start_height : int
        Minimum vertical cell coordinate.
    stop_height : int
        Maximum vertical cell coordinate.

    Attributes
    ----------
    start_width : int
        Minimum horizontal cell coordinate.
    stop_width : int
        Maximum horizontal cell coordinate.
    start_height : int
        Minimum vertical cell coordinate.
    stop_height : int
        Maximum vertical cell coordinate.
    pos : tuple[int, int]
        Current grid coordinates (x, y) of the food item.
    """

    def __init__(
        self,
        start_width: int = 0,
        stop_width: int = 0,
        start_height: int = 0,
        stop_height: int = 0,
    ) -> None:
        self.start_width = start_width
        self.stop_width = stop_width
        self.start_height = start_height
        self.stop_height = stop_height
        self.pos: tuple[int, int] = (0, 0)
        self.spawn()

    def spawn(self) -> tuple[int, int]:
        """Spawn the food at a randomly chosen valid board position.

        Returns
        -------
        tuple[int, int]
            The newly chosen (x, y) coordinates.
        """
        self.pos = (
            random.randrange(self.start_width, self.stop_width),  # noqa: S311
            random.randrange(self.start_height, self.stop_height),  # noqa: S311
        )
        return self.pos

    def get_pos(self) -> tuple[int, int]:
        """Retrieve the current board coordinates of the food.

        Returns
        -------
        tuple[int, int]
            Current (x, y) coordinate tuple.
        """
        return self.pos

    def clone(self) -> Food:
        """Create an independent copy of this food prototype.

        Returns
        -------
        Food
            A new Food instance configured with identical spawn boundaries.
        """
        return Food(
            self.start_width,
            self.stop_width,
            self.start_height,
            self.stop_height,
        )


class Spawner:
    """Factory responsible for spawning food entities using the prototype pattern."""

    @staticmethod
    def spawn_food(prototype: Food) -> Food:
        """Spawn a new food item cloned from a prototype.

        Parameters
        ----------
        prototype : Food
            The food prototype object to replicate.

        Returns
        -------
        Food
            The cloned food instance.
        """
        return prototype.clone()
