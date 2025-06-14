"""Refactored renderer implementation with new architecture."""

import curses
from typing import List, Optional
from interfaces.game_interfaces import IRenderer
from core.game_state import GameState, TetrominoState
from core.config_manager import ConfigManager
from core.dependency_injection import Injectable, Container
from core.event_system import EventType, EventHandler, Event, get_event_bus
from core.logger import get_logger, get_error_handler


class CursesRenderer(IRenderer, Injectable, EventHandler):
    """Curses-based renderer implementation with dependency injection."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.config_manager: ConfigManager = None
        self.logger = get_logger()
        self.error_handler = get_error_handler()
        self.event_bus = get_event_bus()
        
        self._initialized = False
        self._color_pairs_initialized = False
        self._display_config = None
    
    def initialize(self, container: Container) -> None:
        """Initialize with dependencies from container."""
        self.config_manager = container.get(ConfigManager)
        self._display_config = self.config_manager.display
        
        # Subscribe to events
        self.event_bus.subscribe_multiple(self)
        
        self._setup_curses()
        self._initialized = True
        
        self.logger.info("CursesRenderer initialized")
    
    def initialize_renderer(self) -> None:
        """Initialize the renderer without dependencies."""
        if not self._initialized:
            self._setup_curses()
            self._initialized = True
    
    def _setup_curses(self) -> None:
        """Set up curses environment."""
        try:
            # Basic curses setup
            curses.curs_set(0)  # Hide cursor
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            
            # Initialize colors if supported
            if curses.has_colors():
                curses.start_color()
                self._initialize_color_pairs()
            else:
                self.logger.warning("Terminal does not support colors")
            
            self.logger.debug("Curses setup completed")
            
        except Exception as e:
            self.error_handler.handle_error(e, "setting up curses", critical=True)
            raise RuntimeError(f"Failed to initialize curses: {e}")
    
    def _initialize_color_pairs(self) -> None:
        """Initialize color pairs from configuration."""
        if self._color_pairs_initialized:
            return
        
        try:
            colors = self._display_config.colors if self._display_config else {}
            
            # Map color names to curses colors
            color_map = {
                1: curses.COLOR_RED,
                2: curses.COLOR_GREEN,
                3: curses.COLOR_YELLOW,
                4: curses.COLOR_BLUE,
                5: curses.COLOR_MAGENTA,
                6: curses.COLOR_CYAN,
                7: curses.COLOR_WHITE,
                8: curses.COLOR_BLACK,
                9: curses.COLOR_WHITE
            }
            
            # Initialize color pairs for each piece type
            for piece_type, color_id in colors.items():
                if piece_type == "ghost":
                    # Ghost piece with special attributes
                    curses.init_pair(color_id, curses.COLOR_WHITE, curses.COLOR_BLACK)
                elif piece_type == "board":
                    # Board border color
                    curses.init_pair(color_id, curses.COLOR_WHITE, curses.COLOR_BLACK)
                else:
                    # Regular piece colors
                    curses_color = color_map.get(color_id, curses.COLOR_WHITE)
                    curses.init_pair(color_id, curses_color, curses.COLOR_BLACK)
            
            self._color_pairs_initialized = True
            self.logger.debug("Color pairs initialized")
            
        except Exception as e:
            self.error_handler.handle_error(e, "initializing color pairs")
            # Use default colors if configuration fails
            self._initialize_default_colors()
    
    def _initialize_default_colors(self) -> None:
        """Initialize default color pairs as fallback."""
        try:
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLACK)
            self._color_pairs_initialized = True
        except Exception as e:
            self.error_handler.handle_error(e, "initializing default colors")
    
    def render_game(self, state: GameState) -> None:
        """Render the complete game state."""
        try:
            if not self._initialized:
                self.initialize()
            
            self.clear_screen()
            
            # Render based on game status
            if state.status.value == "playing":
                self._render_playing_state(state)
            elif state.status.value == "paused":
                self._render_playing_state(state)
                self.render_pause_screen()
            elif state.status.value == "game_over":
                self._render_playing_state(state)
                self.render_game_over_screen(state.score, state.level)
            
            self.refresh()
            
        except Exception as e:
            self.error_handler.handle_error(e, "rendering game state")
    
    def _render_playing_state(self, state: GameState) -> None:
        """Render the main playing state."""
        # Render board with pieces
        if state.current_piece and state.ghost_piece:
            board_with_pieces = self._get_board_with_all_pieces(
                state.board, state.current_piece, state.ghost_piece
            )
        elif state.current_piece:
            board_with_pieces = self._get_board_with_piece(state.board, state.current_piece)
        else:
            board_with_pieces = state.board
        
        self.render_board(board_with_pieces)
        
        # Render next piece
        if state.next_piece:
            self.render_next_piece(state.next_piece)
        
        # Render game info
        self.render_game_info(state.score, state.level, state.lines_cleared)
        
        # Render controls
        self.render_controls_help()
    
    def render_board(self, board: List[List[int]], ghost_piece: Optional[TetrominoState] = None) -> None:
        """Render the game board with optional ghost piece."""
        try:
            if not board:
                return
            
            height = len(board)
            width = len(board[0]) if board else 0
            
            offset_x = self._display_config.board_offset_x if self._display_config else 2
            offset_y = self._display_config.board_offset_y if self._display_config else 2
            
            # Draw border
            self._draw_board_border(width, height, offset_x, offset_y)
            
            # Draw board content
            for y in range(height):
                for x in range(width):
                    screen_x = offset_x + x * 2 + 1
                    screen_y = offset_y + y + 1
                    
                    cell_value = board[y][x]
                    self._draw_board_cell(screen_x, screen_y, cell_value)
            
        except Exception as e:
            self.error_handler.handle_error(e, "rendering board")
    
    def _draw_board_border(self, width: int, height: int, offset_x: int, offset_y: int) -> None:
        """Draw board border."""
        try:
            border_color = self._display_config.colors.get("board", 9) if self._display_config else 9
            
            # Vertical borders
            for y in range(height + 2):
                self.stdscr.addstr(offset_y + y, offset_x, '|', curses.color_pair(border_color))
                self.stdscr.addstr(offset_y + y, offset_x + width * 2 + 1, '|', curses.color_pair(border_color))
            
            # Horizontal border (bottom)
            for x in range(width * 2 + 2):
                self.stdscr.addstr(offset_y + height + 1, offset_x + x, '-', curses.color_pair(border_color))
                
        except Exception as e:
            self.error_handler.handle_error(e, "drawing board border")
    
    def _draw_board_cell(self, x: int, y: int, cell_value: int) -> None:
        """Draw a single board cell."""
        try:
            if cell_value == 0:
                # Empty cell
                self.stdscr.addstr(y, x, '. ')
            elif cell_value == self._display_config.colors.get("ghost", 8) if self._display_config else 8:
                # Ghost piece
                self.stdscr.addstr(y, x, '[]', curses.color_pair(cell_value) | curses.A_DIM)
            else:
                # Regular piece
                self.stdscr.addstr(y, x, '[]', curses.color_pair(cell_value))
                
        except Exception as e:
            self.error_handler.handle_error(e, f"drawing cell at ({x}, {y})")
    
    def render_piece(self, piece: TetrominoState) -> None:
        """Render a tetromino piece."""
        # This method is used for rendering pieces in isolation
        # Main piece rendering is handled in render_board
        pass
    
    def render_next_piece(self, piece: TetrominoState) -> None:
        """Render the next piece preview."""
        try:
            info_offset_x = self._display_config.info_offset_x if self._display_config else 25
            
            self.stdscr.addstr(2, info_offset_x, "Next:")
            
            if piece and piece.shape:
                # Get compact preview of the piece
                preview = self._get_piece_preview(piece)
                
                for row_idx, row in enumerate(preview):
                    for col_idx, cell in enumerate(row):
                        if cell:
                            screen_x = info_offset_x + col_idx * 2
                            screen_y = 3 + row_idx
                            self.stdscr.addstr(screen_y, screen_x, '[]', curses.color_pair(piece.color))
            
        except Exception as e:
            self.error_handler.handle_error(e, "rendering next piece")
    
    def render_game_info(self, score: int, level: int, lines: int) -> None:
        """Render game information (score, level, lines)."""
        try:
            info_offset_x = self._display_config.info_offset_x if self._display_config else 25
            
            self.stdscr.addstr(8, info_offset_x, f"Score: {score}")
            self.stdscr.addstr(9, info_offset_x, f"Level: {level}")
            self.stdscr.addstr(10, info_offset_x, f"Lines: {lines}")
            
        except Exception as e:
            self.error_handler.handle_error(e, "rendering game info")
    
    def render_controls_help(self) -> None:
        """Render controls help information."""
        try:
            info_offset_x = self._display_config.info_offset_x if self._display_config else 25
            
            controls = [
                "Controls:",
                "W/↑: Rotate",
                "A/←: Left",
                "D/→: Right",
                "S/↓: Soft Drop",
                "Space: Hard Drop",
                "P: Pause",
                "Q: Quit"
            ]
            
            for i, control in enumerate(controls):
                self.stdscr.addstr(12 + i, info_offset_x, control)
                
        except Exception as e:
            self.error_handler.handle_error(e, "rendering controls help")
    
    def render_pause_screen(self) -> None:
        """Render pause screen."""
        try:
            height, width = self.stdscr.getmaxyx()
            message = "PAUSED - Press P to continue"
            x = (width - len(message)) // 2
            y = height // 2
            
            self.stdscr.addstr(y, x, message, curses.A_BOLD | curses.A_REVERSE)
            
        except Exception as e:
            self.error_handler.handle_error(e, "rendering pause screen")
    
    def render_game_over_screen(self, final_score: int, final_level: int) -> None:
        """Render game over screen."""
        try:
            height, width = self.stdscr.getmaxyx()
            
            messages = [
                "GAME OVER",
                f"Final Score: {final_score}",
                f"Final Level: {final_level}",
                "Press Q to quit"
            ]
            
            start_y = height // 2 - len(messages) // 2
            
            for i, message in enumerate(messages):
                x = (width - len(message)) // 2
                y = start_y + i
                
                if i == 0:  # "GAME OVER" with special formatting
                    self.stdscr.addstr(y, x, message, curses.A_BOLD | curses.A_BLINK)
                else:
                    self.stdscr.addstr(y, x, message, curses.A_BOLD)
                    
        except Exception as e:
            self.error_handler.handle_error(e, "rendering game over screen")
    
    def clear_screen(self) -> None:
        """Clear the screen."""
        try:
            self.stdscr.clear()
        except Exception as e:
            self.error_handler.handle_error(e, "clearing screen")
    
    def refresh(self) -> None:
        """Refresh the display."""
        try:
            self.stdscr.refresh()
        except Exception as e:
            self.error_handler.handle_error(e, "refreshing display")
    
    def cleanup(self) -> None:
        """Clean up rendering resources."""
        try:
            if self._initialized:
                curses.endwin()
                self._initialized = False
                self.logger.info("Renderer cleaned up")
        except Exception as e:
            self.error_handler.handle_error(e, "cleaning up renderer")
    
    def handle_event(self, event: Event) -> None:
        """Handle events."""
        if event.event_type == EventType.RENDER_REQUESTED:
            state = event.data.get("state")
            if state:
                self.render_game(state)
        elif event.event_type == EventType.CONFIG_CHANGED:
            # Reload display configuration
            self._display_config = self.config_manager.display
            self._color_pairs_initialized = False
            self._initialize_color_pairs()
    
    def get_handled_events(self) -> List[EventType]:
        """Return list of event types this handler processes."""
        return [EventType.RENDER_REQUESTED, EventType.CONFIG_CHANGED]
    
    def _get_board_with_piece(self, board: List[List[int]], piece: TetrominoState) -> List[List[int]]:
        """Get board with piece overlay."""
        board_copy = [row[:] for row in board]
        
        if piece and piece.shape:
            for row_idx, row in enumerate(piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        board_x = piece.x + col_idx
                        board_y = piece.y + row_idx
                        
                        if (0 <= board_y < len(board_copy) and 
                            0 <= board_x < len(board_copy[0])):
                            board_copy[board_y][board_x] = piece.color
        
        return board_copy
    
    def _get_board_with_all_pieces(self, board: List[List[int]], 
                                  current_piece: TetrominoState, 
                                  ghost_piece: TetrominoState) -> List[List[int]]:
        """Get board with both current and ghost pieces."""
        board_copy = [row[:] for row in board]
        
        # Add ghost piece first (lower priority)
        if ghost_piece and ghost_piece.shape:
            ghost_color = self._display_config.colors.get("ghost", 8) if self._display_config else 8
            for row_idx, row in enumerate(ghost_piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        board_x = ghost_piece.x + col_idx
                        board_y = ghost_piece.y + row_idx
                        
                        if (0 <= board_y < len(board_copy) and 
                            0 <= board_x < len(board_copy[0]) and
                            board_copy[board_y][board_x] == 0):  # Only if empty
                            board_copy[board_y][board_x] = ghost_color
        
        # Add current piece on top (higher priority)
        if current_piece and current_piece.shape:
            for row_idx, row in enumerate(current_piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        board_x = current_piece.x + col_idx
                        board_y = current_piece.y + row_idx
                        
                        if (0 <= board_y < len(board_copy) and 
                            0 <= board_x < len(board_copy[0])):
                            board_copy[board_y][board_x] = current_piece.color
        
        return board_copy
    
    def _get_piece_preview(self, piece: TetrominoState) -> List[List[int]]:
        """Get compact preview of piece for display."""
        if not piece or not piece.shape:
            return [[0]]
        
        # Find bounding box of the piece
        min_row, max_row = len(piece.shape), -1
        min_col, max_col = len(piece.shape[0]) if piece.shape else 0, -1
        
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    min_row = min(min_row, row_idx)
                    max_row = max(max_row, row_idx)
                    min_col = min(min_col, col_idx)
                    max_col = max(max_col, col_idx)
        
        if max_row == -1:  # Empty piece
            return [[0]]
        
        # Extract minimal bounding box
        preview = []
        for row_idx in range(min_row, max_row + 1):
            preview_row = []
            for col_idx in range(min_col, max_col + 1):
                preview_row.append(piece.shape[row_idx][col_idx])
            preview.append(preview_row)
        
        return preview