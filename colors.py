"""Color definitions and utilities."""

import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def change_color(
    surface: pygame.Surface, color: tuple[int, ...], width: int, height: int,
) -> pygame.Surface:
    """
    Optimized color addition using Pygame's native C-accelerated BLEND_RGBA_ADD.

    Significantly faster than O(W*H) pixel-by-pixel iterations in Python.

    Returns
    -------
    pygame.Surface
        The updated surface.
    """
    surface.fill(
        (*color, 0), rect=(0, 0, width, height), special_flags=pygame.BLEND_RGBA_ADD,
    )
    return surface
