"""Tests for game state management."""

import unittest
from core.game_state import GameState, GameStateManager, GameStatus, TetrominoState, GameStateError


class TestGameState(unittest.TestCase):
    """Test cases for GameState."""
    
    def test_default_game_state(self):
        """Test default game state creation."""
        state = GameState()
        
        self.assertEqual(state.status, GameStatus.MENU)
        self.assertEqual(state.score, 0)
        self.assertEqual(state.level, 1)
        self.assertEqual(state.board_width, 10)
        self.assertEqual(state.board_height, 20)
        self.assertIsNotNone(state.board)
    
    def test_tetromino_state_creation(self):
        """Test tetromino state creation."""
        shape = [[1, 1], [1, 1]]
        piece = TetrominoState(
            shape_type="O",
            x=3,
            y=0,
            rotation=0,
            shape=shape,
            color=3
        )
        
        self.assertEqual(piece.shape_type, "O")
        self.assertEqual(piece.x, 3)
        self.assertEqual(piece.y, 0)
        self.assertEqual(piece.color, 3)
        self.assertEqual(piece.shape, shape)


class TestGameStateManager(unittest.TestCase):
    """Test cases for GameStateManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = GameStateManager()
    
    def test_initial_state(self):
        """Test initial state management."""
        initial_state = self.manager.current_state
        
        self.assertEqual(initial_state.status, GameStatus.MENU)
        self.assertEqual(initial_state.score, 0)
    
    def test_update_state(self):
        """Test state updates."""
        new_state = self.manager.update_state(score=100, level=2)
        
        self.assertEqual(new_state.score, 100)
        self.assertEqual(new_state.level, 2)
        self.assertEqual(self.manager.current_state.score, 100)
    
    def test_increment_score(self):
        """Test score increment."""
        initial_score = self.manager.current_state.score
        new_state = self.manager.increment_score(50)
        
        self.assertEqual(new_state.score, initial_score + 50)
    
    def test_clear_lines(self):
        """Test line clearing update."""
        initial_lines = self.manager.current_state.lines_cleared
        new_state = self.manager.clear_lines(2)
        
        self.assertEqual(new_state.lines_cleared, initial_lines + 2)
    
    def test_invalid_board_state(self):
        """Test invalid board state validation."""
        invalid_board = [[1, 2], [3]]  # Inconsistent row lengths
        
        with self.assertRaises(GameStateError):
            self.manager.update_board(invalid_board)
    
    def test_reset_game(self):
        """Test game reset."""
        # Update state first
        self.manager.update_state(score=500, level=5, lines_cleared=20)
        
        # Reset game
        reset_state = self.manager.reset_game()
        
        self.assertEqual(reset_state.status, GameStatus.PLAYING)
        self.assertEqual(reset_state.score, 0)
        self.assertEqual(reset_state.level, 1)
        self.assertEqual(reset_state.lines_cleared, 0)
    
    def test_state_history(self):
        """Test state history tracking."""
        # Make several updates
        self.manager.update_state(score=10)
        self.manager.update_state(score=20)
        self.manager.update_state(score=30)
        
        # Check history
        self.assertTrue(self.manager.can_undo())
        previous_state = self.manager.get_previous_state()
        self.assertEqual(previous_state.score, 20)
    
    def test_serialize_state(self):
        """Test state serialization."""
        # Create a piece
        piece = TetrominoState(
            shape_type="T",
            x=5,
            y=2,
            rotation=1,
            shape=[[1, 1, 1], [0, 1, 0]],
            color=5
        )
        
        # Update state with piece
        self.manager.update_state(current_piece=piece, score=123)
        
        # Serialize
        serialized = self.manager.serialize_state()
        
        self.assertEqual(serialized['score'], 123)
        self.assertEqual(serialized['current_piece']['shape_type'], 'T')
        self.assertEqual(serialized['current_piece']['x'], 5)


if __name__ == '__main__':
    unittest.main()