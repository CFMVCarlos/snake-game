"""Snake representation and logic."""

import logging

from common import Controls, Directions
from scoreboard import Scoreboard

logger = logging.getLogger(__name__)


class Snake:
    """
    Represents a snake in the game.

    Parameters
    ----------
    body : list[tuple[int, int]] | None, default=None
        The initial body coordinates.
    controls : int, default=1
        The controls type (1 for arrows, 2 for WASD).
    color : tuple[int, ...] | None, default=None
        The color of the snake.
    """

    def __init__(
        self,
        body: list[tuple[int, int]] | None = None,
        controls: int = 1,
        color: tuple[int, ...] | None = None,
    ) -> None:
        if body is None:
            body = []
        self.snake_body: list[tuple[int, int]] = body
        self.direction: Directions = Directions.RIGHT
        self.snake_length: int = len(body)
        self.dead: bool = False

        self.color: tuple[int, ...] | None = color
        self.score: Scoreboard = Scoreboard()
        self.controls: int = controls

    def move(self, direction: Directions | None = None) -> None:
        """
        Move the snake by one block.

        Parameters
        ----------
        direction : Directions | None, default=None
            The direction to move in.
        """
        if direction:
            self.direction = direction

        new_head = (
            self.snake_body[0][0] + self.direction.value[0],
            self.snake_body[0][1] + self.direction.value[1],
        )

        self.snake_body.insert(0, new_head)

        while len(self.snake_body) > self.snake_length:
            self.snake_body.pop()

    def crashed_into_itself(self) -> None:
        """Check if the snake collided with itself."""
        if self.snake_body.count(self.snake_body[0]) > 1:
            logger.info("Snake eats self")
            self.dead = True

    def kill(self) -> None:
        """Kill the snake."""
        logger.info("Snake died")
        self.dead = True

    def eat(self, food_position: tuple[int, int]) -> bool:
        """
        Check if the snake eats the food.

        Parameters
        ----------
        food_position : tuple[int, int]
            The position of the food.

        Returns
        -------
        bool
            True if the snake ate the food, False otherwise.
        """
        if food_position == self.snake_body[0]:
            self.snake_length += 1
            self.score.update()
            return True
        return False

    def get_score(self) -> int:
        """
        Get the snake's score.

        Returns
        -------
        int
            The score.
        """
        return self.score.get_score()

    def crashed_into_wall(self, width: int, height: int) -> None:
        """
        Check and handle wall collisions by wrapping around.

        Parameters
        ----------
        width : int
            The width of the board.
        height : int
            The height of the board.
        """
        for pos, snake_part in enumerate(self.snake_body):
            self.wall_interaction(pos, snake_part, width, height)

    def wall_interaction(
        self, pos: int, snake_part: tuple[int, int], width: int, height: int,
    ) -> None:
        """
        Handle a single body part's interaction with the wall.

        Parameters
        ----------
        pos : int
            The index of the body part.
        snake_part : tuple[int, int]
            The coordinates of the body part.
        width : int
            The width of the board.
        height : int
            The height of the board.
        """
        x, y = snake_part
        if x > width - 1:
            self.snake_body[pos] = (0, y)
        elif x < 0:
            self.snake_body[pos] = (width - 1, y)
        elif y > height - 1:
            self.snake_body[pos] = (x, 0)
        elif y < 0:
            self.snake_body[pos] = (x, height - 1)

    def confirm_key_input(self, key: int) -> bool:
        """
        Check if the key is a valid control for this snake.

        Parameters
        ----------
        key : int
            The key pressed.

        Returns
        -------
        bool
            True if valid, False otherwise.
        """
        return (self.controls == 1 and key in Controls.KEYS) or (
            self.controls == 2  # noqa: PLR2004
            and key in Controls.WASD
        )

    def check_movement(self, direction: Directions) -> bool:
        """
        Check if the direction change is valid (not 180 degrees).

        Parameters
        ----------
        direction : Directions
            The new direction.

        Returns
        -------
        bool
            True if valid, False otherwise.
        """
        return not (
            (self.direction == Directions.RIGHT and direction == Directions.LEFT)
            or (self.direction == Directions.LEFT and direction == Directions.RIGHT)
            or (self.direction == Directions.UP and direction == Directions.DOWN)
            or (self.direction == Directions.DOWN and direction == Directions.UP)
        )
