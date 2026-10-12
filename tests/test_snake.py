"""Unit tests for Snake game entities, movement, collision, and score logic."""

from __future__ import annotations

import pygame
import pytest

from common import Directions
from food import Food, Spawner
from inputhandler import InputHandler
from scoreboard import Scoreboard
from snake import Snake


@pytest.fixture(scope="session", autouse=True)
def _init_pygame() -> None:
    """Initialize Pygame once for headless testing."""
    pygame.init()


def test_snake_initialization() -> None:
    """Verify snake attributes, default values, and body assignment."""
    snake = Snake(body=[(5, 5), (4, 5), (3, 5)], controls=1)
    assert len(snake.snake_body) == 3
    assert snake.snake_length == 3
    assert snake.direction == Directions.RIGHT
    assert not snake.dead
    assert snake.get_score() == 0


def test_snake_movement() -> None:
    """Verify forward step updates coordinates correctly."""
    snake = Snake(body=[(5, 5), (4, 5)], controls=1)
    snake.move(Directions.UP)
    assert snake.snake_body[0] == (5, 4)
    assert snake.snake_body[1] == (5, 5)
    assert len(snake.snake_body) == 2


def test_snake_reverse_direction_prevention() -> None:
    """Verify that immediate 180-degree reversals are rejected."""
    snake = Snake(body=[(5, 5)], controls=1)
    snake.direction = Directions.RIGHT
    assert not snake.check_movement(Directions.LEFT)
    assert snake.check_movement(Directions.UP)
    assert snake.check_movement(Directions.DOWN)
    assert snake.check_movement(Directions.RIGHT)


def test_snake_wall_wrap() -> None:
    """Verify snake wraps around all 4 board edges."""
    board_w, board_h = 20, 15
    snake = Snake(body=[(19, 5)], controls=1)
    snake.move(Directions.RIGHT)
    assert snake.snake_body[0] == (20, 5)
    snake.crashed_into_wall(board_w, board_h)
    assert snake.snake_body[0] == (0, 5)

    # Wrap left
    snake = Snake(body=[(0, 5)], controls=1)
    snake.move(Directions.LEFT)
    assert snake.snake_body[0] == (-1, 5)
    snake.crashed_into_wall(board_w, board_h)
    assert snake.snake_body[0] == (19, 5)

    # Wrap top
    snake = Snake(body=[(5, 0)], controls=1)
    snake.move(Directions.UP)
    assert snake.snake_body[0] == (5, -1)
    snake.crashed_into_wall(board_w, board_h)
    assert snake.snake_body[0] == (5, 14)


def test_snake_eat_and_grow() -> None:
    """Verify eating food increments score and target length."""
    snake = Snake(body=[(5, 5)], controls=1)
    food_pos = (5, 5)
    assert snake.eat(food_pos) is True
    assert snake.get_score() == 1
    assert snake.snake_length == 2

    # Wrong position does not eat
    assert snake.eat((10, 10)) is False


def test_snake_self_collision() -> None:
    """Verify collision is triggered when head overlaps body."""
    snake = Snake(body=[(5, 5), (4, 5), (4, 6), (5, 6), (5, 5)], controls=1)
    snake.crashed_into_itself()
    assert snake.dead is True


def test_food_spawn_and_clone() -> None:
    """Verify food spawning limits and prototype cloning."""
    food = Food(start_width=0, stop_width=10, start_height=0, stop_height=10)
    pos = food.get_pos()
    assert 0 <= pos[0] < 10
    assert 0 <= pos[1] < 10

    spawner = Spawner()
    cloned = spawner.spawn_food(food)
    assert isinstance(cloned, Food)
    assert cloned.start_width == food.start_width
    assert cloned.stop_width == food.stop_width


def test_scoreboard() -> None:
    """Verify scoreboard counter and reset."""
    board = Scoreboard()
    assert board.get_score() == 0
    board.update()
    board.update()
    assert board.get_score() == 2
    board.reset()
    assert board.get_score() == 0


def test_input_handler() -> None:
    """Verify input handler key translations."""
    handler = InputHandler()
    assert handler.handle_input(pygame.K_w) == (pygame.K_w, Directions.UP)
    assert handler.handle_input(pygame.K_UP) == (pygame.K_UP, Directions.UP)
    assert handler.handle_input(pygame.K_d) == (pygame.K_d, Directions.RIGHT)
    assert handler.handle_input(pygame.K_SPACE) == (pygame.K_SPACE, None)
