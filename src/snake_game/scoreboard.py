"""Score tracking component for the snake game."""

from __future__ import annotations


class Scoreboard:
    """Manages player score tracking and incremental updates.

    Attributes
    ----------
    score : int
        Current accumulated score.
    """

    def __init__(self) -> None:
        self.score: int = 0

    def update(self) -> None:
        """Increment the current score by one point."""
        self.score += 1

    def get_score(self) -> int:
        """Retrieve the current score value.

        Returns
        -------
        int
            Current score.
        """
        return self.score

    def reset(self) -> None:
        """Reset the score back to zero."""
        self.score = 0
