"""Main game engine implementation with dependency injection."""

import time
import uuid
from typing import Optional
from interfaces.game_interfaces import (
    IGameEngine, IRenderer, IInputHandler, IGameBoard, 
    ITetrominoFactory, IScoreCalculator
)
from core.game_state import GameState, GameStatus, GameStateManager
from core.config_manager import ConfigManager
from core.dependency_injection import Injectable, Container
from core.event_system import EventType, EventHandler, Event, get_event_bus
from core.logger import get_logger, get_error_handler, get_game_logger


class ScoreCalculator(IScoreCalculator, Injectable):
    """Score calculation implementation."""
    
    def __init__(self):
        self.config_manager: ConfigManager = None
        self.logger = get_logger()
    
    def initialize(self, container: Container) -> None:
        """Initialize with dependencies."""
        self.config_manager = container.get(ConfigManager)
    
    def calculate_line_score(self, lines_cleared: int, level: int) -> int:
        """Calculate score for cleared lines."""
        scoring = self.config_manager.scoring
        score_table = {
            1: scoring.single_line,
            2: scoring.double_line,
            3: scoring.triple_line,
            4: scoring.tetris
        }
        return score_table.get(lines_cleared, 0) * level
    
    def calculate_soft_drop_score(self, lines_dropped: int) -> int:
        """Calculate score for soft drop."""
        return lines_dropped  # 1 point per line
    
    def calculate_hard_drop_score(self, lines_dropped: int) -> int:
        """Calculate score for hard drop."""
        return lines_dropped * 2  # 2 points per line
    
    def calculate_level(self, lines_cleared: int) -> int:
        """Calculate level based on lines cleared."""
        lines_per_level = self.config_manager.game.lines_per_level
        return max(1, lines_cleared // lines_per_level + 1)
    
    def calculate_fall_speed(self, level: int) -> int:
        """Calculate fall speed based on level."""
        game_config = self.config_manager.game
        return max(
            game_config.min_fall_speed,
            game_config.initial_fall_speed - (level - 1) * game_config.fall_speed_increment
        )


class TetrisGameEngine(IGameEngine, Injectable, EventHandler):
    """Main Tetris game engine with dependency injection."""
    
    def __init__(self):
        # Dependencies (injected)
        self.config_manager: ConfigManager = None
        self.renderer: IRenderer = None
        self.input_handler: IInputHandler = None
        self.game_board: IGameBoard = None
        self.tetromino_factory: ITetrominoFactory = None
        self.score_calculator: IScoreCalculator = None
        
        # Core components
        self.logger = get_logger()
        self.error_handler = get_error_handler()
        self.game_logger = get_game_logger()
        self.event_bus = get_event_bus()
        self.state_manager = GameStateManager()
        
        # Game state
        self._running = False
        self._session_id: Optional[str] = None
        self._last_update_time = 0
        self._last_fall_time = 0
        self._initialized = False
    
    def initialize(self, container: Container) -> None:
        """Initialize with dependencies from container."""
        self.config_manager = container.get(ConfigManager)
        self.renderer = container.get(IRenderer)
        self.input_handler = container.get(IInputHandler)
        self.game_board = container.get(IGameBoard)
        self.tetromino_factory = container.get(ITetrominoFactory)
        self.score_calculator = container.get(IScoreCalculator)
        
        # Subscribe to events
        self.event_bus.subscribe_multiple(self)
        
        self._initialized = True
        self.logger.info("TetrisGameEngine initialized")
    
    def initialize(self) -> None:
        """Initialize the game engine."""
        if not self._initialized:
            raise RuntimeError("Game engine must be initialized with dependency container")
    
    def start_game(self) -> None:
        """Start a new game."""
        try:
            if not self._initialized:
                raise RuntimeError("Game engine not initialized")
            
            # Generate session ID and start logging
            self._session_id = str(uuid.uuid4())[:8]
            self.game_logger.start_game_session(self._session_id)
            
            # Reset game state
            self.state_manager.reset_game()
            self.game_board.reset()
            
            # Spawn initial pieces
            current_piece = self.tetromino_factory.create_random_piece()
            next_piece = self.tetromino_factory.create_random_piece()
            ghost_piece = self.game_board.get_ghost_piece_position(current_piece)
            
            # Update state with initial pieces
            self.state_manager.update_state(
                status=GameStatus.PLAYING,
                current_piece=current_piece,
                next_piece=next_piece,
                ghost_piece=ghost_piece
            )
            
            # Initialize timing
            current_time = time.time() * 1000
            self._last_update_time = current_time
            self._last_fall_time = current_time
            
            self._running = True
            
            # Publish game start event
            self.event_bus.publish_event(
                EventType.GAME_STARTED,
                {"session_id": self._session_id},
                "GameEngine"
            )
            
            self.logger.info(f"Game started - Session: {self._session_id}")
            self.game_logger.log_piece_spawned(current_piece.shape_type)
            
        except Exception as e:
            self.error_handler.handle_error(e, "starting game", critical=True)
            raise RuntimeError(f"Failed to start game: {e}")
    
    def pause_game(self) -> None:
        """Pause the current game."""
        try:
            current_state = self.state_manager.current_state
            
            if current_state.status == GameStatus.PLAYING:
                self.state_manager.update_state(status=GameStatus.PAUSED)
                
                self.event_bus.publish_event(
                    EventType.GAME_PAUSED,
                    {"session_id": self._session_id},
                    "GameEngine"
                )
                
                self.logger.info("Game paused")
                
        except Exception as e:
            self.error_handler.handle_error(e, "pausing game")
    
    def resume_game(self) -> None:
        """Resume the paused game."""
        try:
            current_state = self.state_manager.current_state
            
            if current_state.status == GameStatus.PAUSED:
                self.state_manager.update_state(status=GameStatus.PLAYING)
                
                # Reset timing to prevent time jump
                current_time = time.time() * 1000
                self._last_update_time = current_time
                self._last_fall_time = current_time
                
                self.event_bus.publish_event(
                    EventType.GAME_RESUMED,
                    {"session_id": self._session_id},
                    "GameEngine"
                )
                
                self.logger.info("Game resumed")
                
        except Exception as e:
            self.error_handler.handle_error(e, "resuming game")
    
    def end_game(self) -> None:
        """End the current game."""
        try:
            current_state = self.state_manager.current_state
            
            if current_state.status != GameStatus.GAME_OVER:
                self.state_manager.update_state(status=GameStatus.GAME_OVER)
            
            self._running = False
            
            # End game logging
            if self._session_id:
                self.game_logger.end_game_session(current_state.score, current_state.level)
            
            self.event_bus.publish_event(
                EventType.GAME_OVER,
                {
                    "session_id": self._session_id,
                    "final_score": current_state.score,
                    "final_level": current_state.level,
                    "lines_cleared": current_state.lines_cleared
                },
                "GameEngine"
            )
            
            self.logger.info(f"Game ended - Final score: {current_state.score}")
            
        except Exception as e:
            self.error_handler.handle_error(e, "ending game")
    
    def update(self, delta_time: float) -> None:
        """Update game state with elapsed time."""
        try:
            current_state = self.state_manager.current_state
            
            if current_state.status != GameStatus.PLAYING:
                return
            
            current_time = time.time() * 1000
            
            # Handle natural falling
            if current_time - self._last_fall_time >= current_state.fall_speed:
                self._handle_natural_fall()
                self._last_fall_time = current_time
            
            # Handle lock delay
            if current_state.is_grounded and current_state.lock_timer > 0:
                if current_time - current_state.lock_timer >= current_state.lock_delay:
                    self._lock_current_piece()
            
            # Render current state
            self.renderer.render_game(current_state)
            
            self._last_update_time = current_time
            
        except Exception as e:
            self.error_handler.handle_error(e, "updating game state")
    
    def handle_input(self, input_key: str) -> None:
        """Handle input key."""
        try:
            current_state = self.state_manager.current_state
            
            if input_key == 'quit':
                self._running = False
                return
            elif input_key == 'pause':
                if current_state.status == GameStatus.PLAYING:
                    self.pause_game()
                elif current_state.status == GameStatus.PAUSED:
                    self.resume_game()
                return
            
            # Only handle game inputs when playing
            if current_state.status != GameStatus.PLAYING:
                return
            
            if input_key == 'move_left':
                self._move_piece(-1, 0)
                self.game_logger.log_piece_moved("left")
            elif input_key == 'move_right':
                self._move_piece(1, 0)
                self.game_logger.log_piece_moved("right")
            elif input_key == 'soft_drop':
                self._move_piece(0, 1)
                self.game_logger.log_piece_moved("down")
            elif input_key == 'hard_drop':
                self._hard_drop_piece()
                self.game_logger.log_piece_dropped("hard")
            elif input_key == 'rotate_right':
                self._rotate_piece("right")
                self.game_logger.log_piece_rotated("right")
            elif input_key == 'rotate_left':
                self._rotate_piece("left")
                self.game_logger.log_piece_rotated("left")
            
        except Exception as e:
            self.error_handler.handle_error(e, f"handling input {input_key}")
    
    def get_current_state(self) -> GameState:
        """Get current game state."""
        return self.state_manager.current_state
    
    def is_running(self) -> bool:
        """Check if game is running."""
        return self._running
    
    def cleanup(self) -> None:
        """Clean up game engine resources."""
        try:
            self._running = False
            
            if self._session_id:
                current_state = self.state_manager.current_state
                self.game_logger.end_game_session(current_state.score, current_state.level)
            
            self.logger.info("Game engine cleaned up")
            
        except Exception as e:
            self.error_handler.handle_error(e, "cleaning up game engine")
    
    def _handle_natural_fall(self) -> None:
        """Handle natural piece falling."""
        current_state = self.state_manager.current_state
        
        if not current_state.current_piece:
            return
        
        # Try to move piece down
        moved_piece = self.tetromino_factory.move_piece(current_state.current_piece, 0, 1)
        
        if self.game_board.is_valid_position(moved_piece):
            # Update piece position
            ghost_piece = self.game_board.get_ghost_piece_position(moved_piece)
            self.state_manager.update_state(
                current_piece=moved_piece,
                ghost_piece=ghost_piece,
                is_grounded=False,
                lock_timer=0,
                move_resets=0
            )
        else:
            # Piece can't move down - start lock delay
            if not current_state.is_grounded:
                self.state_manager.update_state(
                    is_grounded=True,
                    lock_timer=time.time() * 1000
                )
    
    def _move_piece(self, dx: int, dy: int) -> bool:
        """Move current piece by offset."""
        current_state = self.state_manager.current_state
        
        if not current_state.current_piece:
            return False
        
        moved_piece = self.tetromino_factory.move_piece(current_state.current_piece, dx, dy)
        
        if self.game_board.is_valid_position(moved_piece):
            ghost_piece = self.game_board.get_ghost_piece_position(moved_piece)
            
            # Reset lock delay if piece moved while grounded
            new_move_resets = current_state.move_resets
            new_is_grounded = current_state.is_grounded
            new_lock_timer = current_state.lock_timer
            
            if current_state.is_grounded:
                new_move_resets += 1
                if new_move_resets <= current_state.max_move_resets:
                    new_lock_timer = time.time() * 1000  # Reset timer
                else:
                    # Exceeded max resets, lock immediately
                    self._lock_current_piece()
                    return True
            
            self.state_manager.update_state(
                current_piece=moved_piece,
                ghost_piece=ghost_piece,
                move_resets=new_move_resets,
                lock_timer=new_lock_timer
            )
            
            return True
        
        return False
    
    def _rotate_piece(self, direction: str) -> bool:
        """Rotate current piece."""
        current_state = self.state_manager.current_state
        
        if not current_state.current_piece:
            return False
        
        rotated_piece = self.tetromino_factory.rotate_piece(current_state.current_piece, direction)
        
        if self.game_board.is_valid_position(rotated_piece):
            ghost_piece = self.game_board.get_ghost_piece_position(rotated_piece)
            
            # Reset lock delay if piece rotated while grounded
            new_move_resets = current_state.move_resets
            new_lock_timer = current_state.lock_timer
            
            if current_state.is_grounded:
                new_move_resets += 1
                if new_move_resets <= current_state.max_move_resets:
                    new_lock_timer = time.time() * 1000
                else:
                    self._lock_current_piece()
                    return True
            
            self.state_manager.update_state(
                current_piece=rotated_piece,
                ghost_piece=ghost_piece,
                move_resets=new_move_resets,
                lock_timer=new_lock_timer
            )
            
            return True
        
        return False
    
    def _hard_drop_piece(self) -> None:
        """Hard drop current piece."""
        current_state = self.state_manager.current_state
        
        if not current_state.current_piece:
            return
        
        # Calculate drop distance
        ghost_piece = self.game_board.get_ghost_piece_position(current_state.current_piece)
        drop_distance = ghost_piece.y - current_state.current_piece.y
        
        # Calculate score for hard drop
        hard_drop_score = self.score_calculator.calculate_hard_drop_score(drop_distance)
        
        # Update piece to ghost position and lock immediately
        self.state_manager.update_state(current_piece=ghost_piece)
        self.state_manager.increment_score(hard_drop_score)
        
        # Lock the piece
        self._lock_current_piece()
    
    def _lock_current_piece(self) -> None:
        """Lock current piece in place."""
        current_state = self.state_manager.current_state
        
        if not current_state.current_piece:
            return
        
        # Place piece on board
        self.game_board.place_piece(current_state.current_piece)
        
        # Clear completed lines
        lines_cleared = self.game_board.clear_completed_lines()
        
        # Calculate score for lines
        if lines_cleared > 0:
            line_score = self.score_calculator.calculate_line_score(lines_cleared, current_state.level)
            self.state_manager.increment_score(line_score)
            self.state_manager.clear_lines(lines_cleared)
            self.game_logger.log_lines_cleared(lines_cleared, line_score)
        
        # Check for level up
        new_level = self.score_calculator.calculate_level(current_state.lines_cleared + lines_cleared)
        if new_level > current_state.level:
            self.game_logger.log_level_up(new_level)
        
        # Spawn next piece
        next_piece = current_state.next_piece
        new_next_piece = self.tetromino_factory.create_random_piece()
        
        # Check game over
        if not self.game_board.is_valid_position(next_piece):
            self.game_logger.log_game_over("board full")
            self.end_game()
            return
        
        ghost_piece = self.game_board.get_ghost_piece_position(next_piece)
        
        # Update state with new pieces
        self.state_manager.update_state(
            current_piece=next_piece,
            next_piece=new_next_piece,
            ghost_piece=ghost_piece,
            is_grounded=False,
            lock_timer=0,
            move_resets=0,
            board=self.game_board.get_board()
        )
        
        self.game_logger.log_piece_spawned(next_piece.shape_type)
    
    def handle_event(self, event: Event) -> None:
        """Handle events."""
        if event.event_type == EventType.CONFIG_CHANGED:
            self.logger.info("Configuration changed, updating game settings")
            # Could reload settings here if needed
    
    def get_handled_events(self) -> list:
        """Return list of event types this handler processes."""
        return [EventType.CONFIG_CHANGED]