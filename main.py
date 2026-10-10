"""Main entry point for the snake game."""

from typing import Any

import pygame

import colors
import inputhandler
from common import Directions
from food import Food, Spawner
from snake import Snake
from sprites import FoodSprite, SnakeSprite


def init_game(
    width: int, height: int, scale: int,
) -> tuple[
    pygame.Surface,
    pygame.time.Clock,
    list[Snake],
    list[Food],
    pygame.sprite.Group[Any],
    pygame.font.Font,
    pygame.mixer.Sound,
    pygame.Surface,
]:
    """
    Initialize game components.

    Parameters
    ----------
    width : int
        The width of the board.
    height : int
        The height of the board.
    scale : int
        The scale of the game.

    Returns
    -------
    tuple[ \
        pygame.Surface, pygame.time.Clock, list[Snake], list[Food], \
        pygame.sprite.Group[Any], pygame.font.Font, \
        pygame.mixer.Sound, pygame.Surface \
    ]
        The initialized components.
    """
    pygame.init()
    pygame.mixer.init()

    display = pygame.display.set_mode((scale * width, scale * (height + 1)))
    clock = pygame.time.Clock()

    initial_snake_size = 3
    snakes = [
        Snake(
            [
                (width // 2 - x, height // 2 + 1)
                for x in range(initial_snake_size)
            ],
            controls=1,
            color=colors.BLUE,
        ),
        Snake(
            [
                (width // 2 - x, height // 2 - 1)
                for x in range(initial_snake_size)
            ],
            controls=2,
            color=colors.RED,
        ),
    ]

    food_spawner = Spawner()
    food_amount = 2
    food_prototype = Food(stop_width=width, stop_height=height)
    foods = [food_spawner.spawn_food(food_prototype) for _ in range(food_amount)]

    all_sprites: pygame.sprite.Group[Any] = pygame.sprite.Group()
    for snake in snakes:
        all_sprites.add(SnakeSprite(snake, width, height, scale))
    for f in foods:
        all_sprites.add(FoodSprite(f, width, height, scale))

    score_font = pygame.font.Font(None, 28)

    eat_sound = pygame.mixer.Sound("eat_sound.wav")
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(loops=-1)

    bg = pygame.image.load("background.png").convert()
    bg = pygame.transform.scale(bg, (width * scale, height * scale))

    return display, clock, snakes, foods, all_sprites, score_font, eat_sound, bg


def handle_events(
    snakes: list[Snake],
    key_pressed: inputhandler.InputHandler,
    game_paused: bool,  # noqa: FBT001
) -> tuple[bool, int, Directions | tuple[int, int]]:
    """
    Handle Pygame events.

    Parameters
    ----------
    snakes : list[Snake]
        The list of snakes.
    key_pressed : inputhandler.InputHandler
        The input handler.
    game_paused : bool
        The current pause state.

    Returns
    -------
    tuple[bool, int, Directions | tuple[int, int]]
        The new pause state, key, and direction.
    """
    direction: Directions | tuple[int, int] = (0, 0)
    key = 0

    if pygame.event.get(pygame.QUIT):
        for snake in snakes:
            snake.kill()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            key, direction = key_pressed.handle_input(event.key)
            if event.key == pygame.K_ESCAPE:
                for snake in snakes:
                    snake.kill()
            elif event.key == pygame.K_SPACE:
                game_paused = not game_paused

    return game_paused, key, direction


class GameStateUpdater:
    """
    Helper class to update the game state without passing too many arguments.

    Parameters
    ----------
    width : int
        The width of the board.
    height : int
        The height of the board.
    eat_sound : pygame.mixer.Sound
        The sound to play when food is eaten.
    """

    def __init__(self, width: int, height: int, eat_sound: pygame.mixer.Sound) -> None:
        self.width = width
        self.height = height
        self.eat_sound = eat_sound

    def update(
        self,
        snakes: list[Snake],
        foods: list[Food],
        direction: Directions | tuple[int, int],
        key: int,
    ) -> None:
        """
        Update game logic.

        Parameters
        ----------
        snakes : list[Snake]
            The list of snakes.
        foods : list[Food]
            The list of food items.
        direction : Directions | tuple[int, int]
            The current direction input.
        key : int
            The current key input.
        """
        for snake in snakes:
            if snake.dead:
                continue

            if (
                isinstance(direction, Directions)
                and snake.confirm_key_input(key)
                and snake.check_movement(direction)
            ):
                snake.move(direction)
            else:
                snake.move()

            snake.crashed_into_wall(self.width, self.height)
            snake.crashed_into_itself()

            for f in foods:
                if snake.eat(f.get_pos()):
                    self.eat_sound.play()
                    while f.spawn() in snake.snake_body:
                        pass


class GameRenderer:
    """
    Helper class to render the game state without passing too many arguments.

    Parameters
    ----------
    display : pygame.Surface
        The display surface.
    bg : pygame.Surface
        The background surface.
    score_font : pygame.font.Font
        The font for the score.
    width : int
        The width of the board.
    height : int
        The height of the board.
    scale : int
        The scale of the game.
    """

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        display: pygame.Surface,
        bg: pygame.Surface,
        score_font: pygame.font.Font,
        width: int,
        height: int,
        scale: int,
    ) -> None:
        self.display = display
        self.bg = bg
        self.score_font = score_font
        self.width = width
        self.height = height
        self.scale = scale

    def render(
        self,
        all_sprites: pygame.sprite.Group[Any],
        snakes: list[Snake],
    ) -> None:
        """
        Render the game state to the display.

        Parameters
        ----------
        all_sprites : pygame.sprite.Group[Any]
            The sprite group containing all game entities.
        snakes : list[Snake]
            The list of snakes.
        """
        self.display.fill("white")
        self.display.blit(self.bg, (0, 0))
        all_sprites.update()
        all_sprites.draw(self.display)

        pygame.draw.rect(
            self.display,
            colors.GRAY,
            pygame.Rect(
                0, self.scale * self.height, self.scale * self.width, self.scale,
            ),
        )
        for pos, snake in enumerate(snakes):
            score_text = f"Snake{pos}: {snake.get_score()}"
            self.display.blit(
                self.score_font.render(score_text, antialias=True, color=colors.GREEN),
                (pos * 150, self.scale * self.height),
            )

        pygame.display.flip()


def main(width: int, height: int, scale: int) -> None:
    """
    Run the main game loop.

    Parameters
    ----------
    width : int
        The width of the game board in cells.
    height : int
        The height of the game board in cells.
    scale : int
        The pixel scale for each cell.
    """
    (
        display,
        clock,
        snakes,
        foods,
        all_sprites,
        score_font,
        eat_sound,
        bg,
    ) = init_game(width, height, scale)

    key_pressed = inputhandler.InputHandler()
    game_paused = True

    updater = GameStateUpdater(width, height, eat_sound)
    renderer = GameRenderer(display, bg, score_font, width, height, scale)

    while not all(snake.dead for snake in snakes):
        game_paused, key, direction = handle_events(snakes, key_pressed, game_paused)

        if not game_paused:
            updater.update(snakes, foods, direction, key)

        renderer.render(all_sprites, snakes)
        clock.tick(15)

    pygame.quit()


if __name__ == "__main__":
    main(40, 30, 20)
