"""Classic multiplayer Snake game built with Pygame."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

import pygame

from snake_game import colors, inputhandler
from snake_game.common import GameState
from snake_game.food import Food, Spawner
from snake_game.snake import Snake
from snake_game.sprites import FoodSprite, SnakeSprite

logger = logging.getLogger(__name__)

INITIAL_SNAKE_SIZE: Final[int] = 3
FOOD_AMOUNT: Final[int] = 2
FPS: Final[int] = 15

MODE_SOLO: Final[int] = 1
MODE_VERSUS: Final[int] = 2

WINNER_DRAW: Final[int] = 0
WINNER_PLAYER_1: Final[int] = 1
WINNER_PLAYER_2: Final[int] = 2


class SnakeGame:
    """Manages the lifecycle, state, entities, and rendering of the Snake game.

    Parameters
    ----------
    width : int, default=40
        Width of the game board in cells.
    height : int, default=30
        Height of the game board in cells.
    scale : int, default=20
        Pixel scale multiplier for each cell.
    two_player : bool, default=False
        Whether to initialize in two-player mode (Arrows vs WASD), by default False.

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
    state : GameState
        Current lifecycle state of the game session.
    menu_selection : int
        Selected game mode in the start screen (1 for Solo, 2 for Versus).
    winner : int | None
        Winning player number (1 or 2), 0 for Draw, or None while in progress.
    display : pygame.Surface
        Primary Pygame display surface.
    clock : pygame.time.Clock
        Frame rate regulator clock.
    running : bool
        Flag controlling the primary application loop.
    input_handler : inputhandler.InputHandler
        Keyboard event interpreter.
    spawner : Spawner
        Food entity spawner.
    snakes : list[Snake]
        Active snake entities in the match.
    foods : list[Food]
        Active collectible food items.
    all_sprites : pygame.sprite.Group[FoodSprite | SnakeSprite]
        Container for visual entity sprites.
    score_font : pygame.font.Font
        HUD score typography font.
    overlay_font : pygame.font.Font
        Status banner typography font.
    title_font : pygame.font.Font
        Start screen headline font.
    menu_font : pygame.font.Font
        Start screen options font.
    hint_font : pygame.font.Font
        Instructional hint typography font.
    eat_sound : pygame.mixer.Sound | None
        Food consumption sound effect.
    bg : pygame.Surface
        Board background surface.
    """

    def __init__(
        self,
        width: int = 40,
        height: int = 30,
        scale: int = 20,
        *,
        two_player: bool = False,
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
        self.title_font: pygame.font.Font = pygame.font.Font(None, 60)
        self.menu_font: pygame.font.Font = pygame.font.Font(None, 34)
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
        self.state: GameState = GameState.MENU
        self.menu_selection: int = MODE_VERSUS if two_player else MODE_SOLO
        self.winner: int | None = None

        self.start_game(two_player=two_player)
        self.state = GameState.MENU

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

    @property
    def game_paused(self) -> bool:
        """Indicate whether the game is currently paused.

        Returns
        -------
        bool
            True if paused, False otherwise.
        """
        return self.state == GameState.PAUSED

    @game_paused.setter
    def game_paused(self, val: bool) -> None:
        self.state = GameState.PAUSED if val else GameState.PLAYING

    @property
    def game_over(self) -> bool:
        """Indicate whether the match has ended.

        Returns
        -------
        bool
            True if match is over, False otherwise.
        """
        return self.state == GameState.GAME_OVER

    @game_over.setter
    def game_over(self, val: bool) -> None:
        self.state = GameState.GAME_OVER if val else GameState.PLAYING

    def get_state(self) -> GameState:
        """Retrieve current session lifecycle state.

        Returns
        -------
        GameState
            Current game state enum variant.
        """
        return self.state

    def start_game(self, *, two_player: bool) -> None:
        """Initialize match entities for the requested mode and begin play.

        Parameters
        ----------
        two_player : bool
            True for 2-player versus mode, False for 1-player solo mode.
        """
        self.two_player = two_player
        self.all_sprites.empty()

        if self.two_player:
            self.snakes = [
                Snake(
                    [
                        (self.width // 2 - x, self.height // 2 + 3)
                        for x in range(INITIAL_SNAKE_SIZE)
                    ],
                    controls=1,
                    color=colors.BLUE,
                ),
                Snake(
                    [
                        (self.width // 2 - x, self.height // 2 - 3)
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

        self.winner = None
        self.state = GameState.PLAYING

    def reset(self) -> None:
        """Restart match using the current game mode configuration."""
        self.start_game(two_player=self.two_player)

    def check_snake_collisions(self) -> None:
        """Evaluate mutual snake collisions and update death flags in 2-player mode."""
        if len(self.snakes) < MODE_VERSUS:
            return

        snake1, snake2 = self.snakes[0], self.snakes[1]
        if snake1.dead and snake2.dead:
            return

        head1 = snake1.snake_body[0] if snake1.snake_body else None
        head2 = snake2.snake_body[0] if snake2.snake_body else None

        if head1 is None or head2 is None:
            return

        # 1. Head-on collision (mutual crash)
        if head1 == head2:
            snake1.kill()
            snake2.kill()
            return

        # 2. Snake 1 crashes into Snake 2's body
        if head1 in snake2.snake_body[1:]:
            snake1.kill()

        # 3. Snake 2 crashes into Snake 1's body
        if head2 in snake1.snake_body[1:]:
            snake2.kill()

    def _handle_menu_key(self, key: int) -> None:
        """Process keyboard navigation on the mode select start screen.

        Parameters
        ----------
        key : int
            Pygame key code constant.
        """
        if key in {pygame.K_UP, pygame.K_w}:
            self.menu_selection = MODE_SOLO
        elif key in {pygame.K_DOWN, pygame.K_s}:
            self.menu_selection = MODE_VERSUS
        elif key == pygame.K_1:
            self.menu_selection = MODE_SOLO
            self.start_game(two_player=False)
        elif key == pygame.K_2:
            self.menu_selection = MODE_VERSUS
            self.start_game(two_player=True)
        elif key in {pygame.K_RETURN, pygame.K_SPACE}:
            self.start_game(two_player=(self.menu_selection == MODE_VERSUS))

    def _handle_paused_key(self, key: int) -> None:
        """Process key input while game physics are paused.

        Parameters
        ----------
        key : int
            Pygame key code constant.
        """
        if key == pygame.K_SPACE:
            self.state = GameState.PLAYING
        elif key == pygame.K_m:
            self.state = GameState.MENU
        elif key == pygame.K_r:
            self.reset()

    def _handle_game_over_key(self, key: int) -> None:
        """Process key input on the game over end screen.

        Parameters
        ----------
        key : int
            Pygame key code constant.
        """
        if key == pygame.K_r:
            self.reset()
        elif key == pygame.K_m:
            self.state = GameState.MENU

    def _handle_playing_key(self, key: int) -> None:
        """Process gameplay direction and pause controls during active match.

        Parameters
        ----------
        key : int
            Pygame key code constant.
        """
        if key == pygame.K_SPACE:
            self.state = GameState.PAUSED
            return
        if key == pygame.K_m:
            self.state = GameState.MENU
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

    def _handle_key(self, key: int) -> None:
        """Dispatch keydown event to the active game state handler.

        Parameters
        ----------
        key : int
            Pygame key code constant.
        """
        if key == pygame.K_ESCAPE:
            if self.state == GameState.MENU:
                self.running = False
            else:
                self.state = GameState.MENU
            return

        if self.state == GameState.MENU:
            self._handle_menu_key(key)
        elif self.state == GameState.PLAYING:
            self._handle_playing_key(key)
        elif self.state == GameState.PAUSED:
            self._handle_paused_key(key)
        elif self.state == GameState.GAME_OVER:
            self._handle_game_over_key(key)

    def handle_events(self) -> None:
        """Process Pygame user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _update_snakes(self) -> None:
        """Advance snake positions and perform collision detection."""
        for snake in self.snakes:
            if not snake.dead:
                snake.move()
                snake.crashed_into_wall(self.width, self.height)
                snake.crashed_into_itself()

        if self.two_player:
            self.check_snake_collisions()

    def _update_food_consumption(self) -> None:
        """Detect and process food pickups by alive snakes."""
        for snake in self.snakes:
            if snake.dead:
                continue
            for food in self.foods:
                if snake.eat(food.get_pos()):
                    if self.eat_sound:
                        self.eat_sound.play()
                    while food.spawn() in snake.snake_body:
                        pass

    def _update_match_status(self) -> None:
        """Evaluate player deaths to determine match completion and winner."""
        if self.two_player:
            snake1, snake2 = self.snakes[0], self.snakes[1]
            if snake1.dead or snake2.dead:
                self.state = GameState.GAME_OVER
                if snake1.dead and snake2.dead:
                    self.winner = WINNER_DRAW
                elif snake1.dead:
                    self.winner = WINNER_PLAYER_2
                else:
                    self.winner = WINNER_PLAYER_1
        elif self.snakes[0].dead:
            self.state = GameState.GAME_OVER
            self.winner = WINNER_DRAW

    def update(self) -> None:
        """Advance game physics, handle collisions, and update scores."""
        if self.state != GameState.PLAYING:
            return

        self._update_snakes()
        self._update_food_consumption()
        self._update_match_status()

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

        # Draw status overlays based on state
        if self.state == GameState.MENU:
            self._render_start_screen()
        elif self.state == GameState.GAME_OVER:
            if self.two_player:
                if self.winner == WINNER_PLAYER_1:
                    self._render_overlay(
                        "PLAYER 1 WINS!",
                        "Player 2 crashed! Press R for Rematch or M for Menu",
                        colors.BLUE,
                    )
                elif self.winner == WINNER_PLAYER_2:
                    self._render_overlay(
                        "PLAYER 2 WINS!",
                        "Player 1 crashed! Press R for Rematch or M for Menu",
                        colors.RED,
                    )
                else:
                    self._render_overlay(
                        "IT'S A DRAW!",
                        "Mutual crash! Press R for Rematch or M for Menu",
                        colors.YELLOW,
                    )
            else:
                score = self.snakes[0].get_score() if self.snakes else 0
                self._render_overlay(
                    "GAME OVER",
                    f"Final Score: {score} | Press R to Retry or M for Menu",
                    colors.RED,
                )
        elif self.state == GameState.PAUSED:
            self._render_overlay(
                "PAUSED",
                "Press SPACE to Play / Pause, R to Restart, or M for Menu",
                colors.GREEN,
            )

        pygame.display.flip()

    def _render_menu_options(self, cx: int, cy: int) -> None:
        """Render selectable mode buttons for the title screen.

        Parameters
        ----------
        cx : int
            Horizontal center pixel coordinate.
        cy : int
            Vertical center pixel coordinate.
        """
        opt1_text = (
            "> 1 PLAYER (SOLO) <"
            if self.menu_selection == MODE_SOLO
            else "  1 PLAYER (SOLO)  "
        )
        opt1_color = colors.YELLOW if self.menu_selection == MODE_SOLO else colors.WHITE
        opt1_surf = self.menu_font.render(opt1_text, True, opt1_color)  # noqa: FBT003
        self.display.blit(opt1_surf, opt1_surf.get_rect(center=(cx, cy - 15)))

        opt2_text = (
            "> 2 PLAYERS (VERSUS) <"
            if self.menu_selection == MODE_VERSUS
            else "  2 PLAYERS (VERSUS)  "
        )
        opt2_color = (
            colors.YELLOW if self.menu_selection == MODE_VERSUS else colors.WHITE
        )
        opt2_surf = self.menu_font.render(opt2_text, True, opt2_color)  # noqa: FBT003
        self.display.blit(opt2_surf, opt2_surf.get_rect(center=(cx, cy + 30)))

    def _render_start_screen(self) -> None:
        """Render arcade title screen with player mode selector card."""
        overlay = pygame.Surface(
            (self.width * self.scale, self.height * self.scale), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        self.display.blit(overlay, (0, 0))

        cx = (self.width * self.scale) // 2
        cy = (self.height * self.scale) // 2

        title_surf = self.title_font.render("SNAKE GAME", True, colors.GREEN)  # noqa: FBT003
        self.display.blit(title_surf, title_surf.get_rect(center=(cx, cy - 120)))

        sub_surf = self.hint_font.render(
            "CLASSIC & MULTIPLAYER ARCADE",
            True,  # noqa: FBT003
            colors.WHITE,
        )
        self.display.blit(sub_surf, sub_surf.get_rect(center=(cx, cy - 80)))

        self._render_menu_options(cx, cy)

        controls_surf = self.hint_font.render(
            "Controls: [UP/DOWN] or [W/S] Choose  |  [ENTER/SPACE] Start",
            True,  # noqa: FBT003
            colors.WHITE,
        )
        self.display.blit(controls_surf, controls_surf.get_rect(center=(cx, cy + 90)))

        rules_surf = self.hint_font.render(
            "P1 (Blue): Arrows  |  P2 (Red): WASD  |  Crash opponent to win!",
            True,  # noqa: FBT003
            colors.GRAY,
        )
        self.display.blit(rules_surf, rules_surf.get_rect(center=(cx, cy + 120)))

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
        overlay.fill((0, 0, 0, 150))
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
    two_player: bool = False,
) -> None:
    """Launch the Snake game with designated grid dimensions.

    Parameters
    ----------
    width : int, default=40
        Width of the game board in cells.
    height : int, default=30
        Height of the game board in cells.
    scale : int, default=20
        Pixel scale multiplier for each cell.
    two_player : bool, default=False
        Whether to enable two-player multiplayer, by default False.
    """
    game = SnakeGame(width=width, height=height, scale=scale, two_player=two_player)
    game.run()


if __name__ == "__main__":
    main(40, 30, 20)
