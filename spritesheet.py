"""Handles sprite sheets."""

import logging

import pygame

import colors

logger = logging.getLogger(__name__)


class SpriteSheet:
    """
    Class to load and extract images from a spritesheet.

    Parameters
    ----------
    filename : str
        The path to the spritesheet image file.

    Raises
    ------
    SystemExit
        If the image file cannot be loaded.
    """

    def __init__(self, filename: str) -> None:
        try:
            self.sheet: pygame.Surface = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            logger.exception("Unable to load spritesheet image: %s", filename)
            raise SystemExit(e) from e

    def image_at(
        self,
        rectangle: tuple[int, int, int, int],
        colorkey: int | tuple[int, int, int] | pygame.Color | None = None,
    ) -> pygame.Surface:
        """
        Load a specific image from a specific rectangle.

        Parameters
        ----------
        rectangle : tuple[int, int, int, int]
            The rectangle (x, y, width, height) to extract.
        colorkey : int | tuple[int, int, int] | pygame.Color | None, default=None
            The color to treat as transparent. If -1, the top-left pixel is used.

        Returns
        -------
        pygame.Surface
            The extracted image.
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
        """
        Load a bunch of images and return them as a list.

        Parameters
        ----------
        rects : list[tuple[int, int, int, int]]
            The list of rectangles to extract.
        colorkey : int | tuple[int, int, int] | pygame.Color | None, default=None
            The color to treat as transparent.

        Returns
        -------
        list[pygame.Surface]
            The extracted images.
        """
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(
        self,
        rect: tuple[int, int, int, int],
        image_count: int,
        colorkey: int | tuple[int, int, int] | pygame.Color | None = None,
    ) -> list[pygame.Surface]:
        """
        Load a whole strip of images, and return them as a list.

        Parameters
        ----------
        rect : tuple[int, int, int, int]
            The starting rectangle.
        image_count : int
            The number of images in the strip.
        colorkey : int | tuple[int, int, int] | pygame.Color | None, default=None
            The color to treat as transparent.

        Returns
        -------
        list[pygame.Surface]
            The extracted images.
        """
        tups = [
            (rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
            for x in range(image_count)
        ]
        return self.images_at(tups, colorkey)

    def set_snake_color(
        self, color: tuple[int, ...], width: int, height: int,
    ) -> None:
        """
        Change the color of the spritesheet.

        Parameters
        ----------
        color : tuple[int, ...]
            The color to apply.
        width : int
            The width of the affected area.
        height : int
            The height of the affected area.
        """
        self.sheet = colors.change_color(self.sheet, color, width, height)
