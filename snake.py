"""Snake entity representation, movement mechanics, and collision handling."""

from __future__ import annotations

import logging

from common import CONTROLS_ARROWS, CONTROLS_WASD, Controls, Directions
from scoreboard import Scoreboard

logger = logging.getLogger(__name__)


class Snake:
    """Represents an active snake player in the game.

    Parameters
    ----------
    body : list[tuple[int, int]] | None
        Initial coordinates list for snake segments, by default empty.
    controls : int
        Input scheme identifier (1 for Arrow keys, 2 for WASD).
    color : tuple[int, ...] | None
        RGB color tuple for the snake sprite, or None for default.

    Attributes
    ----------
    snake_body : list[tuple[int, int]]
        Ordered coordinate tuples representing the snake segments from head to tail.
    direction : Directions
        Current directional movement vector.
    snake_length : int
        Target length of the snake body.
    dead : bool
        Flag indicating if the snake has died.
    color : tuple[int, ...] | None
        Custom RGB color tint.
    score : Scoreboard
        Dedicated scoreboard instance tracking food eaten.
    controls : int
        Assigned control configuration identifier.
    """

    def __init__(
        self,
        body: list[tuple[int, int]] | None = None,
        controls: int = 1,
        color: tuple[int, ...] | None = None,
    ) -> None:
        self.snake_body: list[tuple[int, int]] = list(body) if body is not None else []
        self.direction: Directions = Directions.RIGHT
        self.snake_length: int = len(self.snake_body)
        self.dead: bool = False
        self.color: tuple[int, ...] | None = color
        self.score: Scoreboard = Scoreboard()
        self.controls: int = controls

    def move(self, direction: Directions | None = None) -> None:
        """Advance the snake forward by one grid cell.

        Parameters
        ----------
        direction : Directions | None
            Optional new direction vector to adopt before moving.
        """
        if direction is not None:
            self.direction = direction

        if not self.snake_body:
            return

        head_x, head_y = self.snake_body[0]
        dir_x, dir_y = self.direction.value
        new_head = (head_x + dir_x, head_y + dir_y)

        self.snake_body.insert(0, new_head)
        while len(self.snake_body) > self.snake_length:
            self.snake_body.pop()

    def crashed_into_itself(self) -> None:
        """Check for self-collision and mark the snake as dead if detected."""
        if len(self.snake_body) > 1 and self.snake_body[0] in self.snake_body[1:]:
            logger.info("Snake collided with itself")
            self.dead = True

    def kill(self) -> None:
        """Mark the snake as dead."""
        logger.info("Snake died")
        self.dead = True

    def eat(self, food_position: tuple[int, int]) -> bool:
        """Evaluate if the snake's head consumes food at the target coordinates.

        Parameters
        ----------
        food_position : tuple[int, int]
            Grid coordinates (x, y) of the food item.

        Returns
        -------
        bool
            True if food was eaten, False otherwise.
        """
        if self.snake_body and food_position == self.snake_body[0]:
            self.snake_length += 1
            self.score.update()
            return True
        return False

    def get_score(self) -> int:
        """Retrieve the player's current score.

        Returns
        -------
        int
            Current score tally.
        """
        return self.score.get_score()

    def crashed_into_wall(self, width: int, height: int) -> None:
        """Wrap snake body segments around the screen boundaries.

        Parameters
        ----------
        width : int
            Horizontal board boundary width.
        height : int
            Vertical board boundary height.
        """
        for pos, snake_part in enumerate(self.snake_body):
            self.wall_interaction(pos, snake_part, width, height)

    def wall_interaction(
        self,
        pos: int,
        snake_part: tuple[int, int],
        width: int,
        height: int,
    ) -> None:
        """Wrap an individual body segment past screen boundaries.

        Parameters
        ----------
        pos : int
            Index position in the body list.
        snake_part : tuple[int, int]
            Current (x, y) coordinates of the segment.
        width : int
            Screen boundary width.
        height : int
            Screen boundary height.
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
        """Verify whether a pressed key is bound to this snake's controls.

        Parameters
        ----------
        key : int
            Pygame key code to validate.

        Returns
        -------
        bool
            True if the key belongs to this snake's mapping, False otherwise.
        """
        return (self.controls == CONTROLS_ARROWS and key in Controls.KEYS) or (
            self.controls == CONTROLS_WASD and key in Controls.WASD
        )

    def check_movement(self, direction: Directions) -> bool:
        """Verify that a proposed direction does not perform an immediate 180-degree reversal.

        Parameters
        ----------
        direction : Directions
            Proposed new direction.

        Returns
        -------
        bool
            True if movement is legal, False if it directly reverses course.
        """
        return not (
            (self.direction == Directions.RIGHT and direction == Directions.LEFT)
            or (self.direction == Directions.LEFT and direction == Directions.RIGHT)
            or (self.direction == Directions.UP and direction == Directions.DOWN)
            or (self.direction == Directions.DOWN and direction == Directions.UP)
        )
