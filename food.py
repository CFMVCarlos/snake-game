"""Food and Spawner implementation."""

import random


class Food:
    """
    Represents a food item for the snake.

    Parameters
    ----------
    start_width : int, default=0
        The minimum x coordinate.
    stop_width : int, default=0
        The maximum x coordinate.
    start_height : int, default=0
        The minimum y coordinate.
    stop_height : int, default=0
        The maximum y coordinate.
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
        """
        Spawn the food at a random position.

        Returns
        -------
        tuple[int, int]
            The new position.
        """
        self.pos = (
            random.randrange(self.start_width, self.stop_width),  # noqa: S311
            random.randrange(self.start_height, self.stop_height),  # noqa: S311
        )
        return self.pos

    def get_pos(self) -> tuple[int, int]:
        """
        Get the current position of the food.

        Returns
        -------
        tuple[int, int]
            The current position.
        """
        return self.pos

    def clone(self) -> "Food":
        """
        Clone this food object.

        Returns
        -------
        Food
            A new Food object with the same spawn boundaries.
        """
        return Food(
            self.start_width, self.stop_width, self.start_height, self.stop_height,
        )


class Spawner:
    """Spawns food objects."""

    @staticmethod
    def spawn_food(prototype: Food) -> Food:
        """
        Spawn a new food object based on a prototype.

        Parameters
        ----------
        prototype : Food
            The prototype food to clone.

        Returns
        -------
        Food
            The new food object.
        """
        return prototype.clone()
