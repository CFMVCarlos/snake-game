"""Spritesheet loader and sub-surface extraction utilities."""

from __future__ import annotations

import logging
from pathlib import Path

import pygame

from snake_game import colors

logger = logging.getLogger(__name__)


class SpriteSheet:
    """Manages loading and clipping individual sprites from a master sheet.

    Parameters
    ----------
    filename : str
        Path to the spritesheet image asset on disk.

    Attributes
    ----------
    sheet : pygame.Surface
        The loaded master surface with alpha channel transparency.

    Raises
    ------
    SystemExit
        If the spritesheet image cannot be found or loaded by Pygame.
    """

    def __init__(self, filename: str) -> None:
        target_path = Path(filename)
        if not target_path.exists():
            local_fallback = Path(__file__).resolve().parent / target_path.name
            if local_fallback.exists():
                target_path = local_fallback

        try:
            self.sheet: pygame.Surface = pygame.image.load(
                str(target_path)
            ).convert_alpha()
        except pygame.error as err:
            logger.exception("Unable to load spritesheet image: %s", target_path)
            raise SystemExit(err) from err

    def image_at(
        self,
        rectangle: tuple[int, int, int, int],
        colorkey: int | tuple[int, int, int] | pygame.Color | None = None,
    ) -> pygame.Surface:
        """Extract a single sprite surface bounded by a rectangle.

        Parameters
        ----------
        rectangle : tuple[int, int, int, int]
            Bounding box tuple (x, y, width, height) on the master sheet.
        colorkey : int | tuple[int, int, int] | pygame.Color | None, default=None
            Optional color key for transparent pixels, or -1 for top-left pixel.

        Returns
        -------
        pygame.Surface
            Extracted sub-surface sprite.
        """
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)

        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)

        return image

    def images_at(
        self,
        rects: list[tuple[int, int, int, int]],
        colorkey: int | tuple[int, int, int] | pygame.Color | None = None,
    ) -> list[pygame.Surface]:
        """Extract multiple sprite surfaces from a list of bounding rectangles.

        Parameters
        ----------
        rects : list[tuple[int, int, int, int]]
            List of bounding box tuples to extract.
        colorkey : int | tuple[int, int, int] | pygame.Color | None, default=None
            Optional color key for transparency.

        Returns
        -------
        list[pygame.Surface]
            List of extracted sprite surfaces.
        """
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(
        self,
        rect: tuple[int, int, int, int],
        image_count: int,
        colorkey: int | tuple[int, int, int] | pygame.Color | None = None,
    ) -> list[pygame.Surface]:
        """Extract a horizontal row strip of sequentially spaced sprites.

        Parameters
        ----------
        rect : tuple[int, int, int, int]
            Initial sprite bounding box (x, y, width, height).
        image_count : int
            Number of consecutive sprites in the horizontal strip.
        colorkey : int | tuple[int, int, int] | pygame.Color | None, default=None
            Optional color key for transparency.

        Returns
        -------
        list[pygame.Surface]
            List of extracted strip surfaces.
        """
        tups = [
            (rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
            for x in range(image_count)
        ]
        return self.images_at(tups, colorkey)

    def set_snake_color(
        self,
        color: tuple[int, ...],
        width: int,
        height: int,
    ) -> None:
        """Apply custom color blending to the underlying spritesheet surface.

        Parameters
        ----------
        color : tuple[int, ...]
            RGB color tuple to blend into the spritesheet.
        width : int
            Boundary width of the spritesheet to color.
        height : int
            Boundary height of the spritesheet to color.
        """
        self.sheet = colors.change_color(self.sheet, color, width, height)
