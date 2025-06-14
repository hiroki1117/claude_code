"""Tests for tetromino factory."""

import unittest
import tempfile
import os
import json
from core.config_manager import ConfigManager
from core.dependency_injection import Container
from components.tetromino_factory import TetrominoFactory


class TestTetrominoFactory(unittest.TestCase):
    """Test cases for TetrominoFactory."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        # Create test configuration with minimal pieces
        self.test_config = {
            "tetrominoes": {
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
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
        
        # Set up dependency injection
        self.container = Container()
        config_manager = ConfigManager(self.config_file)
        self.container.register_instance(ConfigManager, config_manager)
        
        self.factory = TetrominoFactory()
        self.factory.initialize(self.container)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_create_specific_piece(self):
        """Test creating specific piece types."""
        i_piece = self.factory.create_piece("I")
        
        self.assertEqual(i_piece.shape_type, "I")
        self.assertEqual(i_piece.color, 6)
        self.assertEqual(i_piece.x, 3)  # Default spawn position
        self.assertEqual(i_piece.y, 0)
        self.assertEqual(i_piece.rotation, 0)
    
    def test_create_random_piece(self):
        """Test creating random pieces."""
        piece = self.factory.create_random_piece()
        
        self.assertIn(piece.shape_type, ["I", "O"])
        self.assertIn(piece.color, [6, 3])
    
    def test_get_available_types(self):
        """Test getting available piece types."""
        types = self.factory.get_available_types()
        
        self.assertEqual(set(types), {"I", "O"})
    
    def test_rotate_piece(self):
        """Test piece rotation."""
        i_piece = self.factory.create_piece("I")
        
        # Rotate right
        rotated = self.factory.rotate_piece(i_piece, "right")
        self.assertEqual(rotated.rotation, 1)
        self.assertEqual(rotated.shape_type, "I")
        
        # Rotate left from original
        rotated_left = self.factory.rotate_piece(i_piece, "left")
        self.assertEqual(rotated_left.rotation, 1)  # Should wrap around
    
    def test_move_piece(self):
        """Test piece movement."""
        piece = self.factory.create_piece("I")
        
        # Move right
        moved = self.factory.move_piece(piece, 1, 0)
        self.assertEqual(moved.x, piece.x + 1)
        self.assertEqual(moved.y, piece.y)
        
        # Move down
        moved_down = self.factory.move_piece(piece, 0, 2)
        self.assertEqual(moved_down.x, piece.x)
        self.assertEqual(moved_down.y, piece.y + 2)
    
    def test_invalid_piece_type(self):
        """Test creating invalid piece type."""
        with self.assertRaises(ValueError):
            self.factory.create_piece("INVALID")
    
    def test_invalid_rotation_direction(self):
        """Test invalid rotation direction."""
        piece = self.factory.create_piece("I")
        
        with self.assertRaises(ValueError):
            self.factory.rotate_piece(piece, "invalid")
    
    def test_get_piece_size(self):
        """Test getting piece size."""
        size = self.factory.get_piece_size("I")
        self.assertEqual(size, (4, 4))
        
        # Unknown piece should return default
        size = self.factory.get_piece_size("UNKNOWN")
        self.assertEqual(size, (4, 4))
    
    def test_validate_piece_configuration(self):
        """Test piece configuration validation."""
        # Valid configuration
        self.assertTrue(self.factory.validate_piece_configuration("I"))
        self.assertTrue(self.factory.validate_piece_configuration("O"))
        
        # Invalid configuration
        self.assertFalse(self.factory.validate_piece_configuration("UNKNOWN"))
    
    def test_get_piece_preview(self):
        """Test getting piece preview."""
        preview = self.factory.get_piece_preview("O")
        
        # O piece should have a 2x2 preview
        self.assertEqual(len(preview), 2)
        self.assertEqual(len(preview[0]), 2)
        
        # All cells should be filled for O piece
        for row in preview:
            for cell in row:
                self.assertEqual(cell, 1)


if __name__ == '__main__':
    unittest.main()