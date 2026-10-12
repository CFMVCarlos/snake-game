"""Unit tests for Snake game entities, movement, collision, and score logic."""

from __future__ import annotations

import pygame
import pytest

from common import Directions, GameState
from food import Food, Spawner
from inputhandler import InputHandler
from main import (
    MODE_SOLO,
    MODE_VERSUS,
    WINNER_DRAW,
    WINNER_PLAYER_1,
    WINNER_PLAYER_2,
    SnakeGame,
)
from scoreboard import Scoreboard
from snake import Snake
from sprites import SnakeSprite


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


def test_snake_sprite_safe_render() -> None:
    """Verify snake sprite renders safely even when self-colliding."""
    pygame.display.set_mode((200, 200))
    snake = Snake(body=[(10, 10), (10, 9), (10, 10)], controls=1)
    sprite = SnakeSprite(snake, 20, 20, 10)
    sprite.update()
    assert sprite.image.get_width() == 200


def test_start_screen_navigation_and_mode_selection() -> None:
    """Verify start screen navigation and game mode initialization."""
    game = SnakeGame(20, 20, 10)
    assert game.get_state() == GameState.MENU
    assert game.menu_selection == MODE_SOLO

    # Navigate to versus
    game._handle_key(pygame.K_DOWN)
    assert game.menu_selection == MODE_VERSUS

    # Navigate back to solo
    game._handle_key(pygame.K_UP)
    assert game.menu_selection == MODE_SOLO

    # Start solo match
    game._handle_key(pygame.K_RETURN)
    assert game.get_state() == GameState.PLAYING
    assert len(game.snakes) == 1

    # Return to menu with M key
    game._handle_key(pygame.K_m)
    assert game.get_state() == GameState.MENU

    # Select versus with hotkey 2 and start
    game._handle_key(pygame.K_2)
    assert game.get_state() == GameState.PLAYING
    assert len(game.snakes) == 2


def test_versus_snake_mutual_collisions() -> None:
    """Verify collision between two players awards victory to the survivor."""
    game = SnakeGame(20, 20, 10, two_player=True)
    game.start_game(two_player=True)
    snake1, snake2 = game.snakes[0], game.snakes[1]

    # Player 1 crashes into Player 2's body
    snake1.snake_body = [(5, 5), (4, 5)]
    snake2.snake_body = [(10, 10), (5, 5)]
    game.check_snake_collisions()
    assert snake1.dead is True
    assert snake2.dead is False

    game._update_match_status()
    assert game.get_state() == GameState.GAME_OVER
    assert game.winner == WINNER_PLAYER_2

    # Reset and test Player 2 crashing into Player 1's body
    game.start_game(two_player=True)
    s1, s2 = game.snakes[0], game.snakes[1]
    s1.snake_body = [(10, 10), (5, 5)]
    s2.snake_body = [(5, 5), (4, 5)]
    game.check_snake_collisions()
    assert s1.dead is False
    assert s2.dead is True

    game._update_match_status()
    assert game.get_state() == GameState.GAME_OVER
    assert game.winner == WINNER_PLAYER_1


def test_versus_head_on_collision_draw() -> None:
    """Verify simultaneous head-on collision results in a draw."""
    game = SnakeGame(20, 20, 10, two_player=True)
    game.start_game(two_player=True)
    snake1, snake2 = game.snakes[0], game.snakes[1]

    # Both heads on same grid cell
    snake1.snake_body = [(5, 5), (4, 5)]
    snake2.snake_body = [(5, 5), (6, 5)]
    game.check_snake_collisions()
    assert snake1.dead is True
    assert snake2.dead is True

    game._update_match_status()
    assert game.get_state() == GameState.GAME_OVER
    assert game.winner == WINNER_DRAW
