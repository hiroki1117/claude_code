# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

### Main Execution Methods
```bash
python3 main.py              # Full curses-based game
python3 visual_test.py       # Visual demo (curses-free)
python3 test_terminal.py     # Environment check
python3 simple_tetris.py     # Non-curses fallback
```

### Execution Requirements
- Terminal size: minimum 45x25 characters
- Color support required for full experience
- TTY environment needed for curses version
- Fallback options available for restricted environments

## Architecture

This is a modular Tetris implementation using Python's curses library for terminal-based UI.

### Core Components

- **TetrisGame** (`tetris_game.py`) - Main game loop and state management
- **GameBoard** (`game_board.py`) - Board logic, collision detection, line clearing
- **Tetromino** (`tetromino.py`) - Piece shapes, rotations, and movement
- **Renderer** (`renderer.py`) - Terminal display using curses
- **InputHandler** (`input_handler.py`) - Keyboard input processing

### Key Design Patterns

- **Immutable piece movement** - All tetromino operations return new instances rather than modifying existing ones
- **Separation of concerns** - Game logic, rendering, and input handling are cleanly separated
- **Board state management** - Game board maintains its own state and validates piece placement

### Terminal Requirements

- Minimum terminal size: 45x25 characters
- Color support required
- Works best with UTF-8 terminals
- Includes fallback simple version without curses dependencies

### Game Features

- 7 standard tetromino pieces (I, O, T, S, Z, J, L)
- Ghost piece preview showing drop position
- Standard Tetris scoring system
- Level progression every 10 lines cleared
- Pause/resume functionality

### Controls Implementation

Input mapping in `input_handler.py`:
- WASD and arrow keys for movement/rotation
- Space for hard drop
- P for pause, Q for quit
- Non-blocking input with 100ms timeout