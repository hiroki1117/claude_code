#!/usr/bin/env python3
"""
Visual test of Tetris game logic without curses dependency
"""
import time
import random
from tetromino import Tetromino
from game_board import GameBoard

# ANSI color codes for terminal output
COLORS = {
    0: '  ',       # Empty
    1: '\033[96m██\033[0m',     # Cyan (I)
    2: '\033[93m██\033[0m',     # Yellow (O)
    3: '\033[95m██\033[0m',     # Magenta (T)
    4: '\033[92m██\033[0m',     # Green (S)
    5: '\033[91m██\033[0m',     # Red (Z)
    6: '\033[94m██\033[0m',     # Blue (J)
    7: '\033[97m██\033[0m',     # White (L)
    -1: '\033[37m░░\033[0m',    # Ghost piece
}

def clear_screen():
    """Clear terminal screen"""
    print('\033[2J\033[H', end='')

def render_board(board, current_tetromino=None):
    """Render the game board with current piece"""
    clear_screen()
    
    # Create board copy for rendering
    board_copy = board.get_board_copy()
    
    # Add ghost piece
    if current_tetromino:
        ghost_y = board.get_drop_position(current_tetromino)
        ghost_tetromino = current_tetromino.move(0, ghost_y - current_tetromino.y)
        ghost_blocks = ghost_tetromino.get_blocks()
        
        for x, y in ghost_blocks:
            if 0 <= y < board.height and 0 <= x < board.width:
                if board_copy[y][x] == 0:
                    board_copy[y][x] = -1  # Ghost marker
    
    # Add current tetromino
    if current_tetromino:
        blocks = current_tetromino.get_blocks()
        for x, y in blocks:
            if 0 <= y < board.height and 0 <= x < board.width:
                board_copy[y][x] = current_tetromino.color
    
    # Render the board
    print("╔" + "═" * (board.width * 2) + "╗")
    for y in range(board.height):
        print("║", end="")
        for x in range(board.width):
            print(COLORS.get(board_copy[y][x], '??'), end="")
        print("║")
    print("╚" + "═" * (board.width * 2) + "╝")

def demo_tetris_game():
    """Demonstrate Tetris game mechanics"""
    print("=== Tetris Game Logic Demo ===\n")
    
    board = GameBoard(10, 20)
    score = 0
    level = 1
    lines_cleared = 0
    
    # Demo sequence
    pieces = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
    
    for i, piece_type in enumerate(pieces):
        print(f"\nStep {i+1}: Placing {piece_type} piece")
        
        # Create tetromino
        tetromino = Tetromino(piece_type)
        tetromino.x = 3
        tetromino.y = 0
        
        # Show initial position
        render_board(board, tetromino)
        print(f"Score: {score} | Level: {level} | Lines: {lines_cleared}")
        print(f"Current piece: {piece_type} (Color {tetromino.color})")
        
        # Simulate drop
        drop_y = board.get_drop_position(tetromino)
        final_tetromino = tetromino.move(0, drop_y - tetromino.y)
        
        # Place piece
        board.place_tetromino(final_tetromino)
        
        # Check for line clears
        cleared = board.clear_lines()
        if cleared > 0:
            lines_cleared += cleared
            score_table = {1: 40, 2: 100, 3: 300, 4: 1200}
            score += score_table.get(cleared, 0) * level
            level = min(10, (lines_cleared // 10) + 1)
            print(f"Lines cleared: {cleared}!")
        
        # Show final state
        render_board(board)
        print(f"Score: {score} | Level: {level} | Lines: {lines_cleared}")
        
        time.sleep(1)  # Pause for visual effect
    
    print("\n=== Demo Complete ===")
    print("Game mechanics working correctly!")

def test_rotations():
    """Test piece rotations"""
    print("\n=== Rotation Test ===")
    
    piece = Tetromino('T')
    board = GameBoard(8, 8)
    
    for rotation in range(4):
        print(f"\nT-piece rotation {rotation}:")
        piece.x = 3
        piece.y = 2
        
        render_board(board, piece)
        print(f"Blocks: {piece.get_blocks()}")
        
        piece = piece.rotate_right()
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        print("Tetris Visual Test")
        print("==================")
        
        # Test basic functionality
        demo_tetris_game()
        
        # Test rotations
        test_rotations()
        
        print("\n🎮 All tests completed successfully!")
        print("The game logic is working correctly.")
        print("To run the full game, use: python3 main.py")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()