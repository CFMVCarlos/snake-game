"""Keyboard input translation to snake direction commands."""

from __future__ import annotations

import pygame

from common import Directions


class InputHandler:
    """Translates Pygame key events into directional game movement.

    Attributes
    ----------
    command : dict[int, Directions]
        Mapping from Pygame key codes to Directions enum variants.
    """

    def __init__(self) -> None:
        self.command: dict[int, Directions] = {
            pygame.K_w: Directions.UP,
            pygame.K_s: Directions.DOWN,
            pygame.K_a: Directions.LEFT,
            pygame.K_d: Directions.RIGHT,
            pygame.K_UP: Directions.UP,
            pygame.K_DOWN: Directions.DOWN,
            pygame.K_LEFT: Directions.LEFT,
            pygame.K_RIGHT: Directions.RIGHT,
        }

    def handle_input(self, key: int) -> tuple[int, Directions | None]:
        """Translate a pressed key code into a directional command.

        Parameters
        ----------
        key : int
            Pygame key code constant.

        Returns
        -------
        tuple[int, Directions | None]
            Tuple containing the key code and the corresponding Direction,
            or None if the key is not mapped to a direction.
        """
        return (key, self.command.get(key, None))

    def handleInput(  # noqa: N802
        self, key: int
    ) -> tuple[int, Directions | tuple[int, int]]:
        """Legacy camelCase wrapper for backward compatibility.

        Parameters
        ----------
        key : int
            Pygame key code constant.

        Returns
        -------
        tuple[int, Directions | tuple[int, int]]
            Tuple containing the key and mapped direction or (0, 0).
        """
        return (key, self.command.get(key, (0, 0)))
