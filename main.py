"""Classic multiplayer Snake game built with Pygame."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

import pygame

import colors
import inputhandler
from food import Food, Spawner
from snake import Snake
from sprites import FoodSprite, SnakeSprite

logger = logging.getLogger(__name__)

INITIAL_SNAKE_SIZE: Final[int] = 3
FOOD_AMOUNT: Final[int] = 2
FPS: Final[int] = 15


class SnakeGame:
    """Manages the lifecycle, state, entities, and rendering of the Snake game.

    Parameters
    ----------
    width : int
        Width of the game board in cells.
    height : int
        Height of the game board in cells.
    scale : int
        Pixel scale multiplier for each cell.
    two_player : bool
        Whether to initialize in two-player mode (Arrows vs WASD), by default True.

    Attributes
    ----------
    width : int
        Board grid cell width.
    height : int
        Board grid cell height.
    scale : int
        Pixel scale per cell.
    two_player : bool
        Flag indicating two-player mode.
    display : pygame.Surface
        Primary Pygame display surface.
    clock : pygame.time.Clock
        Frame rate regulator clock.
    running : bool
        Flag controlling the primary application loop.
    game_paused : bool
        Flag indicating whether game physics are paused.
    game_over : bool
        Flag indicating whether all players have died.
    snakes : list[Snake]
        Active snake entities in the match.
    foods : list[Food]
        Active collectible food items.
    all_sprites : pygame.sprite.Group[FoodSprite | SnakeSprite]
        Container for visual entity sprites.
    """

    def __init__(
        self,
        width: int = 40,
        height: int = 30,
        scale: int = 20,
        *,
        two_player: bool = True,
    ) -> None:
        self.width = width
        self.height = height
        self.scale = scale
        self.two_player = two_player

        pygame.init()
        pygame.mixer.init()

        # Window height includes 1 extra cell row for the scoreboard bar
        self.display: pygame.Surface = pygame.display.set_mode((
            scale * width,
            scale * (height + 1),
        ))
        pygame.display.set_caption("Multiplayer Snake Game")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        # Load fonts
        self.score_font: pygame.font.Font = pygame.font.Font(None, 28)
        self.overlay_font: pygame.font.Font = pygame.font.Font(None, 52)
        self.hint_font: pygame.font.Font = pygame.font.Font(None, 24)

        # Load audio assets safely
        self._init_audio()

        # Load and scale background surface
        self._init_background()

        # Controller and entity state
        self.input_handler = inputhandler.InputHandler()
        self.spawner = Spawner()
        self.snakes: list[Snake] = []
        self.foods: list[Food] = []
        self.all_sprites: pygame.sprite.Group[FoodSprite | SnakeSprite] = (
            pygame.sprite.Group()
        )

        self.running: bool = True
        self.game_paused: bool = True
        self.game_over: bool = False

        self.reset()

    def _init_audio(self) -> None:
        """Load game sound effects and background music if available."""
        eat_path = Path("eat_sound.wav")
        if eat_path.exists():
            self.eat_sound: pygame.mixer.Sound | None = pygame.mixer.Sound(
                str(eat_path)
            )
        else:
            self.eat_sound = None

        music_path = Path("background_music.mp3")
        if music_path.exists():
            try:
                pygame.mixer.music.load(str(music_path))
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(loops=-1)
            except pygame.error:
                logger.warning("Could not initialize background music")

    def _init_background(self) -> None:
        """Load and resize the board background texture."""
        bg_path = Path("background.png")
        if bg_path.exists():
            raw_bg = pygame.image.load(str(bg_path)).convert()
            self.bg: pygame.Surface = pygame.transform.scale(
                raw_bg, (self.width * self.scale, self.height * self.scale)
            )
        else:
            self.bg = pygame.Surface((
                self.width * self.scale,
                self.height * self.scale,
            ))
            self.bg.fill(colors.WHITE)

    def reset(self) -> None:
        """Reinitialize entities, snakes, food, and game state flags."""
        self.all_sprites.empty()

        if self.two_player:
            self.snakes = [
                Snake(
                    [
                        (self.width // 2 - x, self.height // 2 + 1)
                        for x in range(INITIAL_SNAKE_SIZE)
                    ],
                    controls=1,
                    color=colors.BLUE,
                ),
                Snake(
                    [
                        (self.width // 2 - x, self.height // 2 - 1)
                        for x in range(INITIAL_SNAKE_SIZE)
                    ],
                    controls=2,
                    color=colors.RED,
                ),
            ]
        else:
            self.snakes = [
                Snake(
                    [
                        (self.width // 2 - x, self.height // 2)
                        for x in range(INITIAL_SNAKE_SIZE)
                    ],
                    controls=1,
                    color=colors.BLUE,
                )
            ]

        food_prototype = Food(stop_width=self.width, stop_height=self.height)
        self.foods = [
            self.spawner.spawn_food(food_prototype) for _ in range(FOOD_AMOUNT)
        ]

        for s in self.snakes:
            self.all_sprites.add(SnakeSprite(s, self.width, self.height, self.scale))
        for f in self.foods:
            self.all_sprites.add(FoodSprite(f, self.width, self.height, self.scale))

        self.game_paused = True
        self.game_over = False

    def _handle_key(self, key: int) -> None:
        """Process a single keydown event.

        Parameters
        ----------
        key : int
            Pygame key code constant.
        """
        if key == pygame.K_ESCAPE:
            self.running = False
            return

        if key == pygame.K_SPACE and not self.game_over:
            self.game_paused = not self.game_paused
            return

        if key == pygame.K_r:
            self.reset()
            return

        cmd_key, direction = self.input_handler.handle_input(key)
        if direction is not None:
            for snake in self.snakes:
                if (
                    not snake.dead
                    and snake.confirm_key_input(cmd_key)
                    and snake.check_movement(direction)
                ):
                    snake.next_direction = direction

    def handle_events(self) -> None:
        """Process Pygame user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def update(self) -> None:
        """Advance game physics, handle collisions, and update scores."""
        if self.game_paused or self.game_over:
            return

        all_dead = True
        for snake in self.snakes:
            if snake.dead:
                continue

            all_dead = False
            snake.move()
            snake.crashed_into_wall(self.width, self.height)
            snake.crashed_into_itself()

            for food in self.foods:
                if snake.eat(food.get_pos()):
                    if self.eat_sound:
                        self.eat_sound.play()
                    while food.spawn() in snake.snake_body:
                        pass

        if all_dead:
            self.game_over = True

    def render(self) -> None:
        """Render board entities, scoreboard bar, and overlay text."""
        self.display.fill(colors.WHITE)
        self.display.blit(self.bg, (0, 0))

        self.all_sprites.update()
        self.all_sprites.draw(self.display)

        # Draw scoreboard separator bar
        pygame.draw.rect(
            self.display,
            colors.GRAY,
            pygame.Rect(
                0,
                self.scale * self.height,
                self.scale * self.width,
                self.scale,
            ),
        )

        # Draw player scores
        for pos, snake in enumerate(self.snakes):
            status = " [DEAD]" if snake.dead else ""
            score_text = f"P{pos + 1} Score: {snake.get_score()}{status}"
            score_color = colors.RED if snake.dead else colors.GREEN
            text_surf = self.score_font.render(score_text, True, score_color)  # noqa: FBT003
            self.display.blit(text_surf, (pos * 180 + 10, self.scale * self.height + 2))

        # Draw status overlays
        if self.game_over:
            self._render_overlay(
                "GAME OVER", "Press R to Restart or ESC to Quit", colors.RED
            )
        elif self.game_paused:
            self._render_overlay("PAUSED", "Press SPACE to Play / Pause", colors.GREEN)

        pygame.display.flip()

    def _render_overlay(
        self, title: str, subtitle: str, color: tuple[int, ...]
    ) -> None:
        """Render centered HUD status card banner with semi-transparent backdrop.

        Parameters
        ----------
        title : str
            Headline text.
        subtitle : str
            Instructional subtext.
        color : tuple[int, ...]
            RGB accent color.
        """
        overlay = pygame.Surface(
            (self.width * self.scale, self.height * self.scale), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 140))
        self.display.blit(overlay, (0, 0))

        title_surf = self.overlay_font.render(title, True, color)  # noqa: FBT003
        title_rect = title_surf.get_rect(
            center=(
                (self.width * self.scale) // 2,
                (self.height * self.scale) // 2 - 20,
            )
        )
        self.display.blit(title_surf, title_rect)

        hint_surf = self.hint_font.render(subtitle, True, colors.WHITE)  # noqa: FBT003
        hint_rect = hint_surf.get_rect(
            center=(
                (self.width * self.scale) // 2,
                (self.height * self.scale) // 2 + 25,
            )
        )
        self.display.blit(hint_surf, hint_rect)

    def run(self) -> None:
        """Execute the primary game loop until termination."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()


def main(
    width: int = 40,
    height: int = 30,
    scale: int = 20,
    *,
    two_player: bool = True,
) -> None:
    """Launch the Snake game with designated grid dimensions.

    Parameters
    ----------
    width : int
        Width of the game board in cells.
    height : int
        Height of the game board in cells.
    scale : int
        Pixel scale multiplier for each cell.
    two_player : bool
        Whether to enable two-player multiplayer.
    """
    game = SnakeGame(width=width, height=height, scale=scale, two_player=two_player)
    game.run()


if __name__ == "__main__":
    main(40, 30, 20)
