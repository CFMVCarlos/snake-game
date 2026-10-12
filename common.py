"""Common enumerations and control constants for the snake game."""

from __future__ import annotations

from enum import Enum
from typing import ClassVar, Final

from pygame import K_DOWN, K_LEFT, K_RIGHT, K_UP, K_a, K_d, K_s, K_w


class Directions(Enum):
    """Enumeration representing directional 2D movement vectors."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class GameState(Enum):
    """Lifecycle states for the snake game session."""

    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class Controls:
    """Keybinding collections for player input configurations.

    Attributes
    ----------
    KEYS : ClassVar[list[int]]
        Arrow keys control mappings (Player 1).
    WASD : ClassVar[list[int]]
        WASD keys control mappings (Player 2).
    """

    KEYS: ClassVar[list[int]] = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
    WASD: ClassVar[list[int]] = [K_w, K_s, K_a, K_d]


CONTROLS_ARROWS: Final[int] = 1
CONTROLS_WASD: Final[int] = 2
