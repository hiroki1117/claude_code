"""Centralized game state management for Tetris."""

from dataclasses import dataclass, replace
from typing import Optional, List, Dict, Any
from enum import Enum
import copy


class GameStatus(Enum):
    """Game status enumeration."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    FINISHED = "finished"


@dataclass(frozen=True)
class TetrominoState:
    """Immutable tetromino state."""
    shape_type: str
    x: int
    y: int
    rotation: int
    shape: List[List[int]]
    color: int


@dataclass(frozen=True)
class GameState:
    """Immutable game state representation."""
    
    # Game status
    status: GameStatus = GameStatus.MENU
    
    # Board state
    board: List[List[int]] = None
    board_width: int = 10
    board_height: int = 20
    
    # Current pieces
    current_piece: Optional[TetrominoState] = None
    next_piece: Optional[TetrominoState] = None
    ghost_piece: Optional[TetrominoState] = None
    
    # Game metrics
    score: int = 0
    level: int = 1
    lines_cleared: int = 0
    total_pieces: int = 0
    
    # Timing
    fall_time: int = 0
    fall_speed: int = 500
    lock_delay: int = 500
    lock_timer: int = 0
    
    # Movement state
    is_grounded: bool = False
    move_resets: int = 0
    max_move_resets: int = 15
    
    # Input state
    last_input_time: int = 0
    input_repeat_delay: int = 100
    
    def __post_init__(self):
        if self.board is None:
            # Create empty board
            empty_board = [[0 for _ in range(self.board_width)] 
                          for _ in range(self.board_height)]
            super().__setattr__('board', empty_board)


class GameStateManager:
    """Manages game state transitions and validation."""
    
    def __init__(self, initial_state: Optional[GameState] = None):
        self._current_state = initial_state or GameState()
        self._state_history: List[GameState] = [self._current_state]
        self._max_history_size = 100
    
    @property
    def current_state(self) -> GameState:
        """Get current game state."""
        return self._current_state
    
    def update_state(self, **changes) -> GameState:
        """Create new state with changes and validate it."""
        new_state = replace(self._current_state, **changes)
        
        # Validate the new state
        self._validate_state(new_state)
        
        # Update current state and history
        self._current_state = new_state
        self._add_to_history(new_state)
        
        return new_state
    
    def update_board(self, new_board: List[List[int]]) -> GameState:
        """Update board state with validation."""
        if not self._validate_board(new_board):
            raise GameStateError("Invalid board state")
        
        # Create deep copy to ensure immutability
        board_copy = [row[:] for row in new_board]
        return self.update_state(board=board_copy)
    
    def update_piece(self, piece: TetrominoState, piece_type: str = "current") -> GameState:
        """Update piece state."""
        if piece_type == "current":
            return self.update_state(current_piece=piece)
        elif piece_type == "next":
            return self.update_state(next_piece=piece)
        elif piece_type == "ghost":
            return self.update_state(ghost_piece=piece)
        else:
            raise GameStateError(f"Unknown piece type: {piece_type}")
    
    def increment_score(self, points: int) -> GameState:
        """Increment score and check for level up."""
        new_score = self._current_state.score + points
        new_level = self._calculate_level(new_score, self._current_state.lines_cleared)
        new_fall_speed = self._calculate_fall_speed(new_level)
        
        return self.update_state(
            score=new_score,
            level=new_level,
            fall_speed=new_fall_speed
        )
    
    def clear_lines(self, lines_cleared: int) -> GameState:
        """Update state after clearing lines."""
        new_lines_total = self._current_state.lines_cleared + lines_cleared
        new_level = self._calculate_level(self._current_state.score, new_lines_total)
        new_fall_speed = self._calculate_fall_speed(new_level)
        
        return self.update_state(
            lines_cleared=new_lines_total,
            level=new_level,
            fall_speed=new_fall_speed
        )
    
    def reset_game(self) -> GameState:
        """Reset to initial game state."""
        initial_state = GameState(status=GameStatus.PLAYING)
        self._current_state = initial_state
        self._state_history = [initial_state]
        return initial_state
    
    def get_previous_state(self, steps_back: int = 1) -> Optional[GameState]:
        """Get previous state from history."""
        if steps_back >= len(self._state_history) or steps_back < 1:
            return None
        return self._state_history[-steps_back - 1]
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self._state_history) > 1
    
    def serialize_state(self) -> Dict[str, Any]:
        """Serialize current state to dictionary."""
        state = self._current_state
        
        # Convert tetromino states to dictionaries
        current_piece_dict = None
        if state.current_piece:
            current_piece_dict = {
                'shape_type': state.current_piece.shape_type,
                'x': state.current_piece.x,
                'y': state.current_piece.y,
                'rotation': state.current_piece.rotation,
                'shape': state.current_piece.shape,
                'color': state.current_piece.color
            }
        
        next_piece_dict = None
        if state.next_piece:
            next_piece_dict = {
                'shape_type': state.next_piece.shape_type,
                'x': state.next_piece.x,
                'y': state.next_piece.y,
                'rotation': state.next_piece.rotation,
                'shape': state.next_piece.shape,
                'color': state.next_piece.color
            }
        
        return {
            'status': state.status.value,
            'board': state.board,
            'board_width': state.board_width,
            'board_height': state.board_height,
            'current_piece': current_piece_dict,
            'next_piece': next_piece_dict,
            'score': state.score,
            'level': state.level,
            'lines_cleared': state.lines_cleared,
            'total_pieces': state.total_pieces,
            'fall_time': state.fall_time,
            'fall_speed': state.fall_speed,
            'lock_delay': state.lock_delay,
            'lock_timer': state.lock_timer,
            'is_grounded': state.is_grounded,
            'move_resets': state.move_resets,
            'max_move_resets': state.max_move_resets
        }
    
    def _validate_state(self, state: GameState) -> None:
        """Validate game state consistency."""
        # Validate board dimensions
        if not self._validate_board(state.board):
            raise GameStateError("Invalid board state")
        
        # Validate score and level
        if state.score < 0:
            raise GameStateError("Score cannot be negative")
        
        if state.level < 1:
            raise GameStateError("Level must be at least 1")
        
        # Validate piece positions
        if state.current_piece:
            if not self._validate_piece_position(state.current_piece, state.board):
                raise GameStateError("Current piece position is invalid")
    
    def _validate_board(self, board: List[List[int]]) -> bool:
        """Validate board structure and contents."""
        if not board:
            return False
        
        expected_height = self._current_state.board_height
        expected_width = self._current_state.board_width
        
        if len(board) != expected_height:
            return False
        
        for row in board:
            if len(row) != expected_width:
                return False
            
            for cell in row:
                if not isinstance(cell, int) or cell < 0:
                    return False
        
        return True
    
    def _validate_piece_position(self, piece: TetrominoState, board: List[List[int]]) -> bool:
        """Validate that piece position is valid on board."""
        # Basic bounds checking
        if piece.x < 0 or piece.y < 0:
            return False
        
        # Check shape doesn't extend beyond board
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = piece.x + col_idx
                    board_y = piece.y + row_idx
                    
                    if (board_x >= len(board[0]) or 
                        board_y >= len(board) or
                        board[board_y][board_x] != 0):
                        return False
        
        return True
    
    def _calculate_level(self, score: int, lines_cleared: int) -> int:
        """Calculate level based on lines cleared."""
        return max(1, lines_cleared // 10 + 1)
    
    def _calculate_fall_speed(self, level: int) -> int:
        """Calculate fall speed based on level."""
        return max(50, 500 - (level - 1) * 50)
    
    def _add_to_history(self, state: GameState) -> None:
        """Add state to history with size limit."""
        self._state_history.append(state)
        
        # Trim history if it exceeds maximum size
        if len(self._state_history) > self._max_history_size:
            self._state_history = self._state_history[-self._max_history_size:]


class GameStateError(Exception):
    """Raised when game state operations fail."""
    pass