"""Pygame sprite representations for snake bodies and food items."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pygame

from common import Directions
from spritesheet import SpriteSheet

if TYPE_CHECKING:
    from food import Food
    from snake import Snake

CELL_SIZE: Final[int] = 64


class FoodSprite(pygame.sprite.Sprite):
    """Visual sprite representing collectible food on the screen.

    Parameters
    ----------
    food : Food
        Food entity model.
    width : int
        Board grid width in cells.
    height : int
        Board grid height in cells.
    scale : int
        Pixel scale multiplier per grid cell.

    Attributes
    ----------
    food : Food
        Target food data model.
    scale : int
        Scale factor in pixels.
    food_image : pygame.Surface
        Scaled apple sprite image.
    image : pygame.Surface
        Transparent full-screen layer for drawing the food.
    rect : pygame.Rect
        Bounding rectangle of the surface layer.
    """

    def __init__(
        self,
        food: Food,
        width: int,
        height: int,
        scale: int,
    ) -> None:
        super().__init__()
        spritesheet = SpriteSheet("snake-graphics.png")

        self.food: Food = food
        self.scale: int = scale

        # Apple sprite located at grid (0, 3) in spritesheet
        food_image_rect = (0, 3 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        raw_food = spritesheet.image_at(food_image_rect, -1)
        self.food_image: pygame.Surface = pygame.transform.scale(
            raw_food, (scale, scale)
        )

        self.image: pygame.Surface = pygame.Surface(
            [width * scale, height * scale], pygame.SRCALPHA
        ).convert_alpha()
        self.rect: pygame.Rect = self.image.get_rect()
        self.update()

    def update(self) -> None:
        """Redraw the food item at its current board coordinates."""
        self.image.fill((0, 0, 0, 0))
        self.image.blit(
            self.food_image,
            (self.scale * self.food.pos[0], self.scale * self.food.pos[1]),
        )


class SnakeSprite(pygame.sprite.Sprite):
    """Visual sprite rendering connected snake body segments, head, and tail.

    Parameters
    ----------
    snake : Snake
        The underlying Snake data model.
    width : int
        Board grid width in cells.
    height : int
        Board grid height in cells.
    scale : int
        Pixel scale multiplier per grid cell.

    Attributes
    ----------
    snake : Snake
        Underlying snake player data model.
    scale : int
        Pixel scale per cell.
    snake_images : dict[tuple[str, Directions] | tuple[Directions, Directions], pygame.Surface]
        Sprite lookup dictionary mapped by body transition direction pairs.
    image : pygame.Surface
        Full-board transparent surface layer for rendering snake body pieces.
    rect : pygame.Rect
        Bounding rectangle of the surface layer.
    """

    def __init__(
        self,
        snake: Snake,
        width: int,
        height: int,
        scale: int,
    ) -> None:
        super().__init__()
        spritesheet = SpriteSheet("snake-graphics.png")

        self.snake: Snake = snake
        self.scale: int = scale

        if snake.color is not None:
            spritesheet.set_snake_color(snake.color, 5 * CELL_SIZE, 4 * CELL_SIZE)

        snake_map: dict[
            tuple[str, Directions] | tuple[Directions, Directions],
            tuple[int, int],
        ] = {
            ("head", Directions.UP): (3, 0),
            ("head", Directions.RIGHT): (4, 0),
            ("head", Directions.LEFT): (3, 1),
            ("head", Directions.DOWN): (4, 1),
            (Directions.UP, Directions.RIGHT): (0, 0),
            (Directions.LEFT, Directions.DOWN): (0, 0),
            (Directions.DOWN, Directions.RIGHT): (0, 1),
            (Directions.LEFT, Directions.UP): (0, 1),
            (Directions.LEFT, Directions.LEFT): (1, 0),
            (Directions.RIGHT, Directions.RIGHT): (1, 0),
            (Directions.RIGHT, Directions.DOWN): (2, 0),
            (Directions.UP, Directions.LEFT): (2, 0),
            (Directions.UP, Directions.UP): (2, 1),
            (Directions.DOWN, Directions.DOWN): (2, 1),
            (Directions.RIGHT, Directions.UP): (2, 2),
            (Directions.DOWN, Directions.LEFT): (2, 2),
            ("tail", Directions.UP): (4, 3),
            ("tail", Directions.DOWN): (3, 2),
            ("tail", Directions.RIGHT): (3, 3),
            ("tail", Directions.LEFT): (4, 2),
        }

        self.snake_images: dict[
            tuple[str, Directions] | tuple[Directions, Directions],
            pygame.Surface,
        ] = {
            key: pygame.transform.scale(
                spritesheet.image_at(
                    (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), -1
                ),
                (scale, scale),
            )
            for key, (col, row) in snake_map.items()
        }

        self.image: pygame.Surface = pygame.Surface(
            [width * scale, height * scale], pygame.SRCALPHA
        ).convert_alpha()
        self.rect: pygame.Rect = self.image.get_rect()
        self.update()

    @staticmethod
    def _get_direction(
        x: int,
        y: int,
        prev_x: int,
        prev_y: int,
    ) -> Directions:
        """Determine movement direction between two adjacent grid coordinates.

        Accounts for wrapping around the game board edges.

        Parameters
        ----------
        x : int
            Current segment x coordinate.
        y : int
            Current segment y coordinate.
        prev_x : int
            Prior segment x coordinate.
        prev_y : int
            Prior segment y coordinate.

        Returns
        -------
        Directions
            The directional vector between the segments.
        """
        direction = Directions.RIGHT
        if x - prev_x == 1:
            direction = Directions.RIGHT
        elif x - prev_x == -1:
            direction = Directions.LEFT
        elif y - prev_y == 1:
            direction = Directions.DOWN
        elif y - prev_y == -1:
            direction = Directions.UP

        # Edge wrap-around compensation
        if x - prev_x > 1:
            direction = Directions.LEFT
        elif x - prev_x < -1:
            direction = Directions.RIGHT
        elif y - prev_y > 1:
            direction = Directions.UP
        elif y - prev_y < -1:
            direction = Directions.DOWN

        return direction

    def update(self) -> None:
        """Render all body parts, head, and tail onto the sprite surface."""
        self.image.fill((0, 0, 0, 0))

        if not self.snake.snake_body:
            return

        prev_x, prev_y = self.snake.snake_body[0]
        prev_dir: Directions | None = None

        # Draw segments from head towards tail
        for x, y in self.snake.snake_body[1:]:
            direction = self._get_direction(x, y, prev_x, prev_y)
            image_key: tuple[str, Directions] | tuple[Directions, Directions]
            if prev_dir is None:
                image_key = ("head", self.snake.direction)
            else:
                image_key = (prev_dir, direction)

            self.image.blit(
                self.snake_images[image_key],
                (self.scale * prev_x, self.scale * prev_y),
            )

            prev_x, prev_y = x, y
            prev_dir = direction

        # Draw tail or single-cell head
        if prev_dir is not None:
            self.image.blit(
                self.snake_images["tail", prev_dir],
                (self.scale * prev_x, self.scale * prev_y),
            )
        else:
            self.image.blit(
                self.snake_images["head", self.snake.direction],
                (self.scale * prev_x, self.scale * prev_y),
            )
