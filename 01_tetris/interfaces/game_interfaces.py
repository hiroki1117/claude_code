"""Abstract interfaces for game components."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from core.game_state import GameState, TetrominoState
from core.event_system import Event


class IRenderer(ABC):
    """Interface for rendering components."""
    
    @abstractmethod
    def initialize_renderer(self) -> None:
        """Initialize the renderer."""
        pass
    
    @abstractmethod
    def render_game(self, state: GameState) -> None:
        """Render the complete game state."""
        pass
    
    @abstractmethod
    def render_board(self, board: List[List[int]], ghost_piece: Optional[TetrominoState] = None) -> None:
        """Render the game board with optional ghost piece."""
        pass
    
    @abstractmethod
    def render_piece(self, piece: TetrominoState) -> None:
        """Render a tetromino piece."""
        pass
    
    @abstractmethod
    def render_next_piece(self, piece: TetrominoState) -> None:
        """Render the next piece preview."""
        pass
    
    @abstractmethod
    def render_game_info(self, score: int, level: int, lines: int) -> None:
        """Render game information (score, level, lines)."""
        pass
    
    @abstractmethod
    def render_controls_help(self) -> None:
        """Render controls help information."""
        pass
    
    @abstractmethod
    def render_pause_screen(self) -> None:
        """Render pause screen."""
        pass
    
    @abstractmethod
    def render_game_over_screen(self, final_score: int, final_level: int) -> None:
        """Render game over screen."""
        pass
    
    @abstractmethod
    def clear_screen(self) -> None:
        """Clear the screen."""
        pass
    
    @abstractmethod
    def refresh(self) -> None:
        """Refresh the display."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up rendering resources."""
        pass


class IInputHandler(ABC):
    """Interface for input handling components."""
    
    @abstractmethod
    def initialize_handler(self) -> None:
        """Initialize the input handler."""
        pass
    
    @abstractmethod
    def get_input(self, timeout_ms: int = 100) -> Optional[str]:
        """Get input with optional timeout."""
        pass
    
    @abstractmethod
    def is_quit_requested(self) -> bool:
        """Check if quit was requested."""
        pass
    
    @abstractmethod
    def is_pause_requested(self) -> bool:
        """Check if pause was requested."""
        pass
    
    @abstractmethod
    def get_movement_input(self) -> Optional[str]:
        """Get movement input (left, right, down)."""
        pass
    
    @abstractmethod
    def get_rotation_input(self) -> Optional[str]:
        """Get rotation input (rotate_left, rotate_right)."""
        pass
    
    @abstractmethod
    def is_hard_drop_requested(self) -> bool:
        """Check if hard drop was requested."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up input handling resources."""
        pass


class IGameBoard(ABC):
    """Interface for game board components."""
    
    @abstractmethod
    def initialize_board(self, width: int, height: int) -> None:
        """Initialize the board with given dimensions."""
        pass
    
    @abstractmethod
    def get_board(self) -> List[List[int]]:
        """Get current board state."""
        pass
    
    @abstractmethod
    def is_valid_position(self, piece: TetrominoState) -> bool:
        """Check if piece position is valid on board."""
        pass
    
    @abstractmethod
    def place_piece(self, piece: TetrominoState) -> None:
        """Place piece on the board."""
        pass
    
    @abstractmethod
    def clear_completed_lines(self) -> int:
        """Clear completed lines and return count."""
        pass
    
    @abstractmethod
    def get_ghost_piece_position(self, piece: TetrominoState) -> TetrominoState:
        """Calculate ghost piece position."""
        pass
    
    @abstractmethod
    def is_game_over(self) -> bool:
        """Check if game over condition is met."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset board to initial state."""
        pass


class ITetrominoFactory(ABC):
    """Interface for tetromino creation."""
    
    @abstractmethod
    def create_random_piece(self) -> TetrominoState:
        """Create a random tetromino piece."""
        pass
    
    @abstractmethod
    def create_piece(self, piece_type: str) -> TetrominoState:
        """Create a specific tetromino piece."""
        pass
    
    @abstractmethod
    def get_available_types(self) -> List[str]:
        """Get list of available piece types."""
        pass
    
    @abstractmethod
    def rotate_piece(self, piece: TetrominoState, direction: str) -> TetrominoState:
        """Rotate a piece in given direction."""
        pass
    
    @abstractmethod
    def move_piece(self, piece: TetrominoState, dx: int, dy: int) -> TetrominoState:
        """Move a piece by given offset."""
        pass


class IGameEngine(ABC):
    """Interface for game engine components."""
    
    @abstractmethod
    def initialize_engine(self) -> None:
        """Initialize the game engine."""
        pass
    
    @abstractmethod
    def start_game(self) -> None:
        """Start a new game."""
        pass
    
    @abstractmethod
    def pause_game(self) -> None:
        """Pause the current game."""
        pass
    
    @abstractmethod
    def resume_game(self) -> None:
        """Resume the paused game."""
        pass
    
    @abstractmethod
    def end_game(self) -> None:
        """End the current game."""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update game state with elapsed time."""
        pass
    
    @abstractmethod
    def handle_input(self, input_key: str) -> None:
        """Handle input key."""
        pass
    
    @abstractmethod
    def get_current_state(self) -> GameState:
        """Get current game state."""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if game is running."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up game engine resources."""
        pass


class IScoreCalculator(ABC):
    """Interface for score calculation."""
    
    @abstractmethod
    def calculate_line_score(self, lines_cleared: int, level: int) -> int:
        """Calculate score for cleared lines."""
        pass
    
    @abstractmethod
    def calculate_soft_drop_score(self, lines_dropped: int) -> int:
        """Calculate score for soft drop."""
        pass
    
    @abstractmethod
    def calculate_hard_drop_score(self, lines_dropped: int) -> int:
        """Calculate score for hard drop."""
        pass
    
    @abstractmethod
    def calculate_level(self, lines_cleared: int) -> int:
        """Calculate level based on lines cleared."""
        pass
    
    @abstractmethod
    def calculate_fall_speed(self, level: int) -> int:
        """Calculate fall speed based on level."""
        pass


class IGameTimer(ABC):
    """Interface for game timing components."""
    
    @abstractmethod
    def start(self) -> None:
        """Start the timer."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the timer."""
        pass
    
    @abstractmethod
    def pause(self) -> None:
        """Pause the timer."""
        pass
    
    @abstractmethod
    def resume(self) -> None:
        """Resume the timer."""
        pass
    
    @abstractmethod
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        pass
    
    @abstractmethod
    def get_elapsed_ms(self) -> int:
        """Get elapsed time in milliseconds."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the timer."""
        pass


class IAudioManager(ABC):
    """Interface for audio management."""
    
    @abstractmethod
    def initialize_audio(self) -> None:
        """Initialize audio system."""
        pass
    
    @abstractmethod
    def play_sound(self, sound_name: str) -> None:
        """Play a sound effect."""
        pass
    
    @abstractmethod
    def play_music(self, music_name: str, loop: bool = True) -> None:
        """Play background music."""
        pass
    
    @abstractmethod
    def stop_music(self) -> None:
        """Stop background music."""
        pass
    
    @abstractmethod
    def set_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up audio resources."""
        pass


class IGamePersistence(ABC):
    """Interface for game state persistence."""
    
    @abstractmethod
    def save_game(self, state: GameState, filename: str) -> bool:
        """Save game state to file."""
        pass
    
    @abstractmethod
    def load_game(self, filename: str) -> Optional[GameState]:
        """Load game state from file."""
        pass
    
    @abstractmethod
    def save_high_scores(self, scores: List[Dict[str, Any]]) -> bool:
        """Save high scores."""
        pass
    
    @abstractmethod
    def load_high_scores(self) -> List[Dict[str, Any]]:
        """Load high scores."""
        pass
    
    @abstractmethod
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save game settings."""
        pass
    
    @abstractmethod
    def load_settings(self) -> Dict[str, Any]:
        """Load game settings."""
        pass