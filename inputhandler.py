"""Handles player input for the game."""

import pygame

from common import Directions


class InputHandler:
    """Class to manage and map keyboard inputs to directions."""

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

    def handle_input(self, key: int) -> tuple[int, Directions | tuple[int, int]]:
        """
        Handle the keyboard input.

        Parameters
        ----------
        key : int
            The key code that was pressed.

        Returns
        -------
        tuple[int, Directions | tuple[int, int]]
            The key code and the corresponding direction,
            or (0, 0) if no direction maps.
        """
        return (key, self.command.get(key, (0, 0)))
