"""Tests for configuration manager."""

import unittest
import tempfile
import os
import json
from core.config_manager import ConfigManager, ConfigurationError


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        # Create test configuration
        self.test_config = {
            "game": {
                "board_width": 10,
                "board_height": 20,
                "initial_fall_speed": 500
            },
            "scoring": {
                "single_line": 40,
                "tetris": 1200
            },
            "tetrominoes": {
                "I": {
                    "shapes": [[[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]]],
                    "color": 6
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_load_existing_config(self):
        """Test loading existing configuration file."""
        config_manager = ConfigManager(self.config_file)
        
        self.assertEqual(config_manager.game.board_width, 10)
        self.assertEqual(config_manager.game.board_height, 20)
        self.assertEqual(config_manager.scoring.single_line, 40)
    
    def test_load_nonexistent_config(self):
        """Test loading non-existent configuration file."""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.json")
        config_manager = ConfigManager(nonexistent_file)
        
        # Should create default config
        self.assertTrue(os.path.exists(nonexistent_file))
        self.assertEqual(config_manager.game.board_width, 10)  # Default value
    
    def test_get_tetromino_config(self):
        """Test getting tetromino configuration."""
        config_manager = ConfigManager(self.config_file)
        
        i_config = config_manager.get_tetromino_config("I")
        self.assertEqual(i_config["color"], 6)
        self.assertEqual(len(i_config["shapes"]), 1)
    
    def test_get_unknown_tetromino(self):
        """Test getting unknown tetromino configuration."""
        config_manager = ConfigManager(self.config_file)
        
        with self.assertRaises(ConfigurationError):
            config_manager.get_tetromino_config("UNKNOWN")
    
    def test_get_all_tetromino_types(self):
        """Test getting all tetromino types."""
        config_manager = ConfigManager(self.config_file)
        
        types = config_manager.get_all_tetromino_types()
        self.assertIn("I", types)
        self.assertEqual(len(types), 1)
    
    def test_invalid_json(self):
        """Test handling invalid JSON file."""
        with open(self.config_file, 'w') as f:
            f.write("invalid json content")
        
        with self.assertRaises(ConfigurationError):
            ConfigManager(self.config_file)


if __name__ == '__main__':
    unittest.main()