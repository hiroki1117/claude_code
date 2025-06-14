"""Refactored game board implementation with new architecture."""

from typing import List, Optional
from interfaces.game_interfaces import IGameBoard
from core.game_state import TetrominoState
from core.config_manager import ConfigManager
from core.dependency_injection import Injectable, Container
from core.event_system import EventType, get_event_bus
from core.logger import get_logger, get_error_handler


class GameBoard(IGameBoard, Injectable):
    """Game board implementation with dependency injection and event system."""
    
    def __init__(self):
        self.config_manager: ConfigManager = None
        self.logger = get_logger()
        self.error_handler = get_error_handler()
        self.event_bus = get_event_bus()
        
        self.width: int = 10
        self.height: int = 20
        self.board: List[List[int]] = []
    
    def initialize(self, container: Container) -> None:
        """Initialize with dependencies from container."""
        self.config_manager = container.get(ConfigManager)
        
        # Get board dimensions from config
        game_config = self.config_manager.game
        self.width = game_config.board_width
        self.height = game_config.board_height
        
        # Initialize board
        self.initialize(self.width, self.height)
        
        self.logger.info(f"GameBoard initialized with size {self.width}x{self.height}")
    
    def initialize(self, width: int, height: int) -> None:
        """Initialize the board with given dimensions."""
        if width <= 0 or height <= 0:
            self.error_handler.handle_validation_error(
                "board_dimensions", f"{width}x{height}", "positive integers"
            )
            raise ValueError("Board dimensions must be positive")
        
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        
        # Publish board initialization event
        self.event_bus.publish_event(
            EventType.BOARD_UPDATED,
            {"action": "initialized", "width": width, "height": height},
            "GameBoard"
        )
        
        self.logger.debug(f"Board initialized with dimensions {width}x{height}")
    
    def get_board(self) -> List[List[int]]:
        """Get current board state."""
        return [row[:] for row in self.board]  # Return deep copy
    
    def is_valid_position(self, piece: TetrominoState) -> bool:
        """Check if piece position is valid on board."""
        if not piece or not piece.shape:
            return False
        
        try:
            for row_idx, row in enumerate(piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:  # If this cell is occupied in the piece
                        board_x = piece.x + col_idx
                        board_y = piece.y + row_idx
                        
                        # Check bounds
                        if board_x < 0 or board_x >= self.width:
                            return False
                        if board_y >= self.height:
                            return False
                        
                        # Check collision with existing pieces (but allow above board)
                        if board_y >= 0 and self.board[board_y][board_x] != 0:
                            return False
            
            return True
            
        except (IndexError, AttributeError) as e:
            self.error_handler.handle_error(e, "validating piece position")
            return False
    
    def place_piece(self, piece: TetrominoState) -> None:
        """Place piece on the board."""
        if not self.is_valid_position(piece):
            raise ValueError("Cannot place piece at invalid position")
        
        try:
            placed_cells = []
            
            for row_idx, row in enumerate(piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        board_x = piece.x + col_idx
                        board_y = piece.y + row_idx
                        
                        if 0 <= board_y < self.height and 0 <= board_x < self.width:
                            self.board[board_y][board_x] = piece.color
                            placed_cells.append((board_x, board_y))
            
            # Publish piece placement event
            self.event_bus.publish_event(
                EventType.PIECE_LOCKED,
                {
                    "piece_type": piece.shape_type,
                    "position": (piece.x, piece.y),
                    "cells_placed": placed_cells
                },
                "GameBoard"
            )
            
            self.logger.debug(f"Placed {piece.shape_type} at ({piece.x}, {piece.y})")
            
        except Exception as e:
            self.error_handler.handle_error(e, "placing piece on board")
            raise RuntimeError(f"Failed to place piece: {e}")
    
    def clear_completed_lines(self) -> int:
        """Clear completed lines and return count."""
        lines_cleared = 0
        cleared_lines = []
        
        try:
            # Find completed lines from bottom to top
            y = self.height - 1
            while y >= 0:
                if self._is_line_complete(y):
                    # Remove the line and add empty line at top
                    del self.board[y]
                    self.board.insert(0, [0 for _ in range(self.width)])
                    lines_cleared += 1
                    cleared_lines.append(y)
                    # Don't decrement y since we removed a line
                else:
                    y -= 1
            
            if lines_cleared > 0:
                # Publish line clear event
                self.event_bus.publish_event(
                    EventType.LINES_CLEARED,
                    {
                        "lines_cleared": lines_cleared,
                        "line_positions": cleared_lines
                    },
                    "GameBoard"
                )
                
                # Publish board update event
                self.event_bus.publish_event(
                    EventType.BOARD_UPDATED,
                    {"action": "lines_cleared", "count": lines_cleared},
                    "GameBoard"
                )
                
                self.logger.info(f"Cleared {lines_cleared} lines")
            
            return lines_cleared
            
        except Exception as e:
            self.error_handler.handle_error(e, "clearing completed lines")
            raise RuntimeError(f"Failed to clear lines: {e}")
    
    def get_ghost_piece_position(self, piece: TetrominoState) -> TetrominoState:
        """Calculate ghost piece position."""
        if not piece:
            return None
        
        try:
            # Start from current position and move down until collision
            ghost_piece = piece
            
            while True:
                # Try to move one position down
                test_piece = TetrominoState(
                    shape_type=ghost_piece.shape_type,
                    x=ghost_piece.x,
                    y=ghost_piece.y + 1,
                    rotation=ghost_piece.rotation,
                    shape=ghost_piece.shape,
                    color=ghost_piece.color
                )
                
                if self.is_valid_position(test_piece):
                    ghost_piece = test_piece
                else:
                    break
            
            return ghost_piece
            
        except Exception as e:
            self.error_handler.handle_error(e, "calculating ghost piece position")
            return piece  # Return original piece as fallback
    
    def is_game_over(self) -> bool:
        """Check if game over condition is met."""
        try:
            # Game over if any cell in the top row is occupied
            return any(self.board[0][x] != 0 for x in range(self.width))
            
        except Exception as e:
            self.error_handler.handle_error(e, "checking game over condition")
            return False
    
    def reset(self) -> None:
        """Reset board to initial state."""
        try:
            self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
            
            # Publish reset event
            self.event_bus.publish_event(
                EventType.BOARD_UPDATED,
                {"action": "reset"},
                "GameBoard"
            )
            
            self.logger.info("Board reset")
            
        except Exception as e:
            self.error_handler.handle_error(e, "resetting board")
            raise RuntimeError(f"Failed to reset board: {e}")
    
    def get_board_with_piece(self, piece: TetrominoState) -> List[List[int]]:
        """Get board state with piece temporarily placed."""
        if not piece:
            return self.get_board()
        
        try:
            # Create copy of current board
            board_copy = self.get_board()
            
            # Add piece to the copy
            for row_idx, row in enumerate(piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        board_x = piece.x + col_idx
                        board_y = piece.y + row_idx
                        
                        if (0 <= board_y < self.height and 
                            0 <= board_x < self.width):
                            board_copy[board_y][board_x] = piece.color
            
            return board_copy
            
        except Exception as e:
            self.error_handler.handle_error(e, "generating board with piece")
            return self.get_board()
    
    def get_board_with_ghost(self, piece: TetrominoState, ghost_piece: TetrominoState) -> List[List[int]]:
        """Get board state with ghost piece overlay."""
        if not piece or not ghost_piece:
            return self.get_board()
        
        try:
            # Create copy of current board
            board_copy = self.get_board()
            
            # Add ghost piece first (with special ghost color)
            ghost_color = self.config_manager.display.colors.get("ghost", 8)
            for row_idx, row in enumerate(ghost_piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        board_x = ghost_piece.x + col_idx
                        board_y = ghost_piece.y + row_idx
                        
                        if (0 <= board_y < self.height and 
                            0 <= board_x < self.width and
                            board_copy[board_y][board_x] == 0):  # Only if empty
                            board_copy[board_y][board_x] = ghost_color
            
            # Add current piece on top
            for row_idx, row in enumerate(piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        board_x = piece.x + col_idx
                        board_y = piece.y + row_idx
                        
                        if (0 <= board_y < self.height and 
                            0 <= board_x < self.width):
                            board_copy[board_y][board_x] = piece.color
            
            return board_copy
            
        except Exception as e:
            self.error_handler.handle_error(e, "generating board with ghost")
            return self.get_board()
    
    def _is_line_complete(self, line_y: int) -> bool:
        """Check if a specific line is complete."""
        if line_y < 0 or line_y >= self.height:
            return False
        
        return all(self.board[line_y][x] != 0 for x in range(self.width))
    
    def get_line_heights(self) -> List[int]:
        """Get height of each column (for AI or statistics)."""
        heights = []
        
        for col in range(self.width):
            height = 0
            for row in range(self.height):
                if self.board[row][col] != 0:
                    height = self.height - row
                    break
            heights.append(height)
        
        return heights
    
    def get_holes_count(self) -> int:
        """Count holes in the board (empty cells with filled cells above)."""
        holes = 0
        
        for col in range(self.width):
            found_block = False
            for row in range(self.height):
                if self.board[row][col] != 0:
                    found_block = True
                elif found_block and self.board[row][col] == 0:
                    holes += 1
        
        return holes
    
    def get_board_statistics(self) -> dict:
        """Get various board statistics."""
        return {
            "height": self.height,
            "width": self.width,
            "filled_cells": sum(1 for row in self.board for cell in row if cell != 0),
            "empty_cells": sum(1 for row in self.board for cell in row if cell == 0),
            "holes": self.get_holes_count(),
            "column_heights": self.get_line_heights(),
            "top_row_filled": any(self.board[0][x] != 0 for x in range(self.width))
        }