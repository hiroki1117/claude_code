"""Configuration-based tetromino factory implementation."""

import random
from typing import List, Dict, Any
from interfaces.game_interfaces import ITetrominoFactory
from core.game_state import TetrominoState
from core.config_manager import ConfigManager
from core.dependency_injection import Injectable, Container
from core.logger import get_logger, get_error_handler


class TetrominoFactory(ITetrominoFactory, Injectable):
    """Factory for creating tetromino pieces from configuration."""
    
    def __init__(self):
        self.config_manager: ConfigManager = None
        self.logger = get_logger()
        self.error_handler = get_error_handler()
        self._piece_types: List[str] = []
        self._shapes_cache: Dict[str, Dict[str, Any]] = {}
    
    def initialize(self, container: Container) -> None:
        """Initialize with dependencies from container."""
        self.config_manager = container.get(ConfigManager)
        self._load_piece_configurations()
        self.logger.info("TetrominoFactory initialized")
    
    def _load_piece_configurations(self) -> None:
        """Load piece configurations from config manager."""
        try:
            self._piece_types = self.config_manager.get_all_tetromino_types()
            
            # Cache all piece configurations
            for piece_type in self._piece_types:
                config = self.config_manager.get_tetromino_config(piece_type)
                self._shapes_cache[piece_type] = config
            
            self.logger.debug(f"Loaded {len(self._piece_types)} tetromino types")
            
        except Exception as e:
            self.error_handler.handle_error(e, "loading tetromino configurations", critical=True)
            # Fallback to hardcoded basic pieces
            self._load_fallback_pieces()
    
    def _load_fallback_pieces(self) -> None:
        """Load fallback pieces if configuration fails."""
        self.logger.warning("Using fallback tetromino configurations")
        
        fallback_pieces = {
            "I": {
                "shapes": [
                    [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
                    [[0,0,1,0], [0,0,1,0], [0,0,1,0], [0,0,1,0]]
                ],
                "color": 6
            },
            "O": {
                "shapes": [
                    [[0,1,1,0], [0,1,1,0], [0,0,0,0], [0,0,0,0]]
                ],
                "color": 3
            },
            "T": {
                "shapes": [
                    [[0,1,0,0], [1,1,1,0], [0,0,0,0], [0,0,0,0]],
                    [[0,1,0,0], [0,1,1,0], [0,1,0,0], [0,0,0,0]],
                    [[0,0,0,0], [1,1,1,0], [0,1,0,0], [0,0,0,0]],
                    [[0,1,0,0], [1,1,0,0], [0,1,0,0], [0,0,0,0]]
                ],
                "color": 5
            }
        }
        
        self._piece_types = list(fallback_pieces.keys())
        self._shapes_cache = fallback_pieces
    
    def create_random_piece(self) -> TetrominoState:
        """Create a random tetromino piece."""
        if not self._piece_types:
            raise RuntimeError("No tetromino types available")
        
        piece_type = random.choice(self._piece_types)
        return self.create_piece(piece_type)
    
    def create_piece(self, piece_type: str) -> TetrominoState:
        """Create a specific tetromino piece."""
        if piece_type not in self._shapes_cache:
            self.error_handler.handle_validation_error(
                "piece_type", piece_type, f"one of {self._piece_types}"
            )
            raise ValueError(f"Unknown piece type: {piece_type}")
        
        try:
            config = self._shapes_cache[piece_type]
            shapes = config["shapes"]
            color = config["color"]
            
            # Start with first rotation (index 0)
            initial_shape = shapes[0]
            
            piece = TetrominoState(
                shape_type=piece_type,
                x=3,  # Default spawn position
                y=0,
                rotation=0,
                shape=initial_shape,
                color=color
            )
            
            self.logger.debug(f"Created piece: {piece_type}")
            return piece
            
        except (KeyError, IndexError) as e:
            self.error_handler.handle_error(e, f"creating piece {piece_type}")
            raise RuntimeError(f"Failed to create piece {piece_type}: {e}")
    
    def get_available_types(self) -> List[str]:
        """Get list of available piece types."""
        return self._piece_types.copy()
    
    def rotate_piece(self, piece: TetrominoState, direction: str) -> TetrominoState:
        """Rotate a piece in given direction."""
        if direction not in ["left", "right"]:
            self.error_handler.handle_validation_error(
                "direction", direction, "left or right"
            )
            raise ValueError(f"Invalid rotation direction: {direction}")
        
        try:
            config = self._shapes_cache[piece.shape_type]
            shapes = config["shapes"]
            num_rotations = len(shapes)
            
            if direction == "right":
                new_rotation = (piece.rotation + 1) % num_rotations
            else:  # left
                new_rotation = (piece.rotation - 1) % num_rotations
            
            new_shape = shapes[new_rotation]
            
            rotated_piece = TetrominoState(
                shape_type=piece.shape_type,
                x=piece.x,
                y=piece.y,
                rotation=new_rotation,
                shape=new_shape,
                color=piece.color
            )
            
            self.logger.debug(f"Rotated piece {piece.shape_type} {direction}")
            return rotated_piece
            
        except (KeyError, IndexError) as e:
            self.error_handler.handle_error(e, f"rotating piece {piece.shape_type}")
            raise RuntimeError(f"Failed to rotate piece: {e}")
    
    def move_piece(self, piece: TetrominoState, dx: int, dy: int) -> TetrominoState:
        """Move a piece by given offset."""
        try:
            moved_piece = TetrominoState(
                shape_type=piece.shape_type,
                x=piece.x + dx,
                y=piece.y + dy,
                rotation=piece.rotation,
                shape=piece.shape,
                color=piece.color
            )
            
            if dx != 0 or dy != 0:
                self.logger.debug(f"Moved piece {piece.shape_type} by ({dx}, {dy})")
            
            return moved_piece
            
        except Exception as e:
            self.error_handler.handle_error(e, f"moving piece {piece.shape_type}")
            raise RuntimeError(f"Failed to move piece: {e}")
    
    def get_spawn_position(self, piece_type: str) -> tuple:
        """Get default spawn position for piece type."""
        # Standard Tetris spawn position
        return (3, 0)
    
    def get_piece_size(self, piece_type: str) -> tuple:
        """Get the bounding box size of a piece type."""
        if piece_type not in self._shapes_cache:
            return (4, 4)  # Default size
        
        try:
            config = self._shapes_cache[piece_type]
            shape = config["shapes"][0]  # Use first rotation
            
            height = len(shape)
            width = len(shape[0]) if shape else 0
            
            return (width, height)
            
        except (KeyError, IndexError):
            return (4, 4)  # Default size
    
    def validate_piece_configuration(self, piece_type: str) -> bool:
        """Validate piece configuration integrity."""
        if piece_type not in self._shapes_cache:
            return False
        
        try:
            config = self._shapes_cache[piece_type]
            
            # Check required fields
            if "shapes" not in config or "color" not in config:
                return False
            
            shapes = config["shapes"]
            if not shapes or not isinstance(shapes, list):
                return False
            
            # Validate each shape
            for shape in shapes:
                if not isinstance(shape, list) or len(shape) != 4:
                    return False
                
                for row in shape:
                    if not isinstance(row, list) or len(row) != 4:
                        return False
                    
                    for cell in row:
                        if not isinstance(cell, int) or cell not in [0, 1]:
                            return False
            
            # Validate color
            color = config["color"]
            if not isinstance(color, int) or color < 1 or color > 9:
                return False
            
            return True
            
        except Exception:
            return False
    
    def reload_configurations(self) -> None:
        """Reload piece configurations from config manager."""
        try:
            self._shapes_cache.clear()
            self._piece_types.clear()
            self._load_piece_configurations()
            self.logger.info("Tetromino configurations reloaded")
            
        except Exception as e:
            self.error_handler.handle_error(e, "reloading tetromino configurations")
            raise RuntimeError(f"Failed to reload configurations: {e}")
    
    def get_piece_preview(self, piece_type: str, max_size: tuple = (4, 2)) -> List[List[int]]:
        """Get a compact preview of a piece for UI display."""
        if piece_type not in self._shapes_cache:
            return [[0]]
        
        try:
            config = self._shapes_cache[piece_type]
            shape = config["shapes"][0]  # Use first rotation
            
            # Find actual bounds of the piece
            min_row, max_row = 4, -1
            min_col, max_col = 4, -1
            
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        min_row = min(min_row, row_idx)
                        max_row = max(max_row, row_idx)
                        min_col = min(min_col, col_idx)
                        max_col = max(max_col, col_idx)
            
            if max_row == -1:  # Empty piece
                return [[0]]
            
            # Extract the minimal bounding box
            preview = []
            for row_idx in range(min_row, max_row + 1):
                preview_row = []
                for col_idx in range(min_col, max_col + 1):
                    preview_row.append(shape[row_idx][col_idx])
                preview.append(preview_row)
            
            return preview
            
        except Exception as e:
            self.error_handler.handle_error(e, f"generating preview for {piece_type}")
            return [[1]]  # Simple fallback