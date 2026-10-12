"""Color definitions and graphical surface blending utilities."""

from __future__ import annotations

from typing import Final

import pygame

# Standard RGB color tuples
BLACK: Final[tuple[int, int, int]] = (0, 0, 0)
WHITE: Final[tuple[int, int, int]] = (255, 255, 255)
GRAY: Final[tuple[int, int, int]] = (127, 127, 127)
RED: Final[tuple[int, int, int]] = (255, 0, 0)
GREEN: Final[tuple[int, int, int]] = (0, 255, 0)
BLUE: Final[tuple[int, int, int]] = (0, 0, 255)
YELLOW: Final[tuple[int, int, int]] = (255, 215, 0)


def change_color(
    surface: pygame.Surface,
    color: tuple[int, ...],
    width: int,
    height: int,
) -> pygame.Surface:
    """Apply uniform color blending using Pygame native BLEND_RGBA_ADD.

    Performs accelerated hardware blending instead of pixel-by-pixel Python iterations.

    Parameters
    ----------
    surface : pygame.Surface
        The target surface to transform.
    color : tuple[int, ...]
        RGB color tuple to add to the surface pixels.
    width : int
        Width of the target area to fill.
    height : int
        Height of the target area to fill.

    Returns
    -------
    pygame.Surface
        The modified surface with blended colors.
    """
    surface.fill(
        (*color, 0),
        rect=(0, 0, width, height),
        special_flags=pygame.BLEND_RGBA_ADD,
    )
    return surface
