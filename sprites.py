"""Sprites for the game."""

import pygame

import colors
from common import Directions
from food import Food
from snake import Snake
from spritesheet import SpriteSheet

CELL_SIZE = 64


class FoodSprite(pygame.sprite.Sprite):
    """
    Sprite representing food in the game.

    Parameters
    ----------
    food : Food
        The food object to represent.
    width : int
        The width of the board.
    height : int
        The height of the board.
    scale : int
        The scale of the game.
    """

    def __init__(self, food: Food, width: int, height: int, scale: int) -> None:
        super().__init__()

        snake_spritesheet = SpriteSheet("snake-graphics.png")

        self.food = food
        self.scale = scale

        food_image_rect = (0, 3 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.food_image = snake_spritesheet.image_at(food_image_rect, -1)
        self.food_image = pygame.transform.scale(self.food_image, (scale, scale))

        self.image = pygame.Surface([width * scale, height * scale], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.update()

    def update(self) -> None:
        """Update the sprite's image."""
        self.image.fill((0, 0, 0, 0))

        self.image.blit(
            self.food_image,
            (self.scale * self.food.pos[0], self.scale * self.food.pos[1]),
        )


class SnakeSprite(pygame.sprite.Sprite):
    """
    Sprite representing a snake in the game.

    Parameters
    ----------
    snake : Snake
        The snake object to represent.
    width : int
        The width of the board.
    height : int
        The height of the board.
    scale : int
        The scale of the game.
    """

    def __init__(self, snake: Snake, width: int, height: int, scale: int) -> None:
        super().__init__()

        snake_spritesheet = SpriteSheet("snake-graphics.png")

        self.snake = snake
        self.scale = scale
        if snake.color:
            snake_spritesheet.set_snake_color(snake.color, 5 * CELL_SIZE, 4 * CELL_SIZE)

        snake_map: dict[
            tuple[str, Directions] | tuple[Directions, Directions], tuple[int, int],
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

        self.snake_images = {
            name: pygame.transform.scale(
                snake_spritesheet.image_at(
                    (a * CELL_SIZE, b * CELL_SIZE, CELL_SIZE, CELL_SIZE), -1,
                ),
                (scale, scale),
            )
            for (name, (a, b)) in snake_map.items()
        }

        self.image = pygame.Surface([width * scale, height * scale], pygame.SRCALPHA)
        if self.snake.color:
            self.image = colors.change_color(
                self.image, self.snake.color, width * scale, height * scale,
            )
        self.update()
        self.rect = self.image.get_rect()

    @staticmethod
    def _get_direction(x: int, y: int, prev_x: int, prev_y: int) -> Directions:
        """
        Calculate the direction from the previous point to the current point.

        Parameters
        ----------
        x : int
            Current x coordinate.
        y : int
            Current y coordinate.
        prev_x : int
            Previous x coordinate.
        prev_y : int
            Previous y coordinate.

        Returns
        -------
        Directions
            The calculated direction.
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

        # Wrap around handling
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
        """Update the sprite's image."""
        self.image.fill((0, 0, 0, 0))

        if not self.snake.snake_body:
            return

        prev_x, prev_y = self.snake.snake_body[0]
        prev_dir = None

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

        if prev_dir is not None:
            self.image.blit(
                self.snake_images["tail", prev_dir],
                (self.scale * prev_x, self.scale * prev_y),
            )
        else:
            # Handle length 1 snake
            self.image.blit(
                self.snake_images["head", self.snake.direction],
                (self.scale * prev_x, self.scale * prev_y),
            )
