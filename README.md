<div align="center">

# 🐍 Multiplayer Snake Game 🎮

<p align="center">
  <strong>A classic retro arcade Snake game built in modern Python with Pygame, featuring local 2-player multiplayer, sprite-based graphics, audio effects, and clean architecture.</strong>
</p>

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.6.1%2B-green?style=for-the-badge&logo=python&logoColor=white)](https://www.pygame.org/)
[![Package Manager](https://img.shields.io/badge/uv-Package%20Manager-DE5FE9?style=for-the-badge&logo=astral&logoColor=white)](https://astral.sh/uv)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-black?style=for-the-badge&logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![Docstrings](https://img.shields.io/badge/Docstrings-NumPy%20%2F%20pydoclint-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpydoc.readthedocs.io/)
[![Type Checker](https://img.shields.io/badge/Type%20Check-ty%20%26%20mypy-2b5b84?style=for-the-badge&logo=typescript&logoColor=white)](https://github.com/astral-sh/ty)
[![Tests](https://img.shields.io/badge/Tests-Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 Overview

**Multiplayer Snake Game** is an arcade desktop game developed in Python using Pygame. It allows two players to compete simultaneously on the same board, racing to consume apples, grow their snakes, and outmaneuver each other.

The project features a decoupled object-oriented architecture (`SnakeGame`), hardware surface color blending, prototype-based food spawning, and comprehensive static type safety.

---

## ✨ Features

- 👥 **Local 2-Player Multiplayer:** Compete head-to-head with Player 1 (Blue snake, Arrow keys) and Player 2 (Red snake, WASD keys).
- 🎨 **Sprite-Based Graphics & Alpha Transparency:** Smooth rendering of snake head, turning body segments, and tail sprites loaded from an authentic spritesheet with alpha channel support.
- 🎵 **Audio & Sound Effects:** Dynamic crunch sound effects on eating food and looping retro background soundtrack.
- ⏸️ **Interactive HUD & Overlays:**
  - Clear **PAUSED** overlay banner when pausing with <kbd>Space</kbd>.
  - **GAME OVER** screen announcing the conclusion of the match.
  - One-touch instant restart with <kbd>R</kbd>.
- 🪟 **Wrapping Boundaries & Self-Collision:** Seamless toroidal screen wrapping with realistic collision detection.
- ⚡ **High-Performance Architecture:** Pure C-accelerated surface blending via `pygame.BLEND_RGBA_ADD` and vectorized coordinate updates.

---

## 🎮 Controls & Keybindings

| Action | Control / Keybinding | Description |
| :--- | :--- | :--- |
| **Player 1 Movement** | <kbd>▲</kbd> <kbd>▼</kbd> <kbd>◄</kbd> <kbd>►</kbd> | Controls the Blue snake direction (Up, Down, Left, Right). |
| **Player 2 Movement** | <kbd>W</kbd> <kbd>S</kbd> <kbd>A</kbd> <kbd>D</kbd> | Controls the Red snake direction (Up, Down, Left, Right). |
| **Play / Pause** | <kbd>Space</kbd> | Toggles pause state during active gameplay. |
| **Restart Game** | <kbd>R</kbd> | Resets board, snakes, food, and scores immediately. |
| **Exit** | <kbd>Esc</kbd> or Window Close | Closes the game cleanly. |

---

## 📂 Project Architecture

```
snake-game/
├── background.png           # Game board background texture
├── background_music.mp3     # Looping background music track
├── eat_sound.wav            # Sound effect triggered when eating food
├── snake-graphics.png       # Master sprite sheet containing snake body segments and apple
├── pyproject.toml           # Modern package configuration, dependencies, and tool settings
├── uv.lock                  # Deterministic dependency lockfile
├── README.md                # Project showcase and developer manual
├── colors.py                # Color palette constants and accelerated surface blending
├── common.py                # Directional enums and keybinding collections
├── food.py                  # Food entity model and Spawner prototype factory
├── inputhandler.py          # Keycode to directional movement command translator
├── main.py                  # Primary SnakeGame class coordinator and main game loop
├── scoreboard.py            # Player score tracking logic
├── snake.py                 # Snake physics, segment lists, wrapping, and collision detection
├── sprites.py               # Pygame Sprite wrappers for Food and animated Snake bodies
├── spritesheet.py           # Sub-surface clipping and color modification utility
└── tests/
    ├── __init__.py          # Test package marker
    └── test_snake.py        # Automated test suite (movement, wrapping, eating, collisions)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python >= 3.13**
- [**uv**](https://docs.astral.sh/uv/) package manager installed

### Installation & Run

1. Clone the repository:
   ```bash
   git clone https://github.com/CFMVCarlos/snake-game.git
   cd snake-game
   ```

2. Synchronize virtual environment and dependencies:
   ```bash
   uv sync
   ```

3. Launch the game:
   ```bash
   uv run python main.py
   ```
   *(The game launches paused. Press <kbd>Space</kbd> to begin!)*

---

## 🧪 Testing & Code Quality

The codebase enforces strict code quality, typing, and docstring standards:

```bash
# Run unit test suite
uv run pytest

# Check code style and formatting
uv run ruff check
uv run ruff format --check

# Verify NumPy docstring compliance
uv run pydoclint .

# Run Astral static type checker
uv run ty check

# Run Mypy static type checker
uv run mypy
```

---

## 📄 License

This project is open-source and licensed under the [MIT License](LICENSE).

Developed with ❤️ by [Carlos Valente](https://github.com/CFMVCarlos).
