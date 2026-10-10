"""Manages the score for the game."""


class Scoreboard:
    """Tracks and updates the score."""

    def __init__(self) -> None:
        self.score: int = 0

    def update(self) -> None:
        """Increment the score."""
        self.score += 1

    def get_score(self) -> int:
        """
        Get the current score.

        Returns
        -------
        int
            The current score.
        """
        return self.score
