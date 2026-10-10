"""Common utilities and enums."""

from enum import Enum
from typing import ClassVar

from pygame import K_DOWN, K_LEFT, K_RIGHT, K_UP, K_a, K_d, K_s, K_w


class Directions(Enum):
    """Enumeration for snake directions."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Controls:
    """Constants for game controls."""

    KEYS: ClassVar[list[int]] = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
    WASD: ClassVar[list[int]] = [K_w, K_s, K_a, K_d]
