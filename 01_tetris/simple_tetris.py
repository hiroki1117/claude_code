#!/usr/bin/env python3
"""
Simple Tetris without curses - for debugging
"""
import time
import random
import os
import sys
import threading
from tetromino import Tetromino
from game_board import GameBoard

# ANSI escape codes for colors
COLORS = {
    0: '\033[0m',      # Reset
    1: '\033[96m',     # Cyan
    2: '\033[93m',     # Yellow  
    3: '\033[95m',     # Magenta
    4: '\033[92m',     # Green
    5: '\033[91m',     # Red
    6: '\033[94m',     # Blue
    7: '\033[97m',     # White
}

class SimpleTetris:
    def __init__(self):
        self.board = GameBoard()
        self.current_tetromino = Tetromino()
        self.next_tetromino = Tetromino()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.running = True
        
        # Set up non-blocking input
        if os.name == 'posix':
            import termios, tty
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())

    def __del__(self):
        if os.name == 'posix':
            import termios
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_input(self):
        if os.name == 'posix':
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.read(1)
        return None

    def render(self):
        self.clear_screen()
        
        # Create board copy for rendering
        board_copy = self.board.get_board_copy()
        
        # Add current tetromino to board
        if self.current_tetromino:
            blocks = self.current_tetromino.get_blocks()
            for x, y in blocks:
                if 0 <= y < self.board.height and 0 <= x < self.board.width:
                    board_copy[y][x] = self.current_tetromino.color
        
        # Print board
        print("+" + "-" * (self.board.width * 2) + "+")
        for y in range(self.board.height):
            print("|", end="")
            for x in range(self.board.width):
                if board_copy[y][x] > 0:
                    color = COLORS.get(board_copy[y][x], COLORS[0])
                    print(f"{color}██{COLORS[0]}", end="")
                else:
                    print("  ", end="")
            print("|")
        print("+" + "-" * (self.board.width * 2) + "+")
        
        # Print stats
        print(f"\nScore: {self.score}")
        print(f"Level: {self.level}")
        print(f"Lines: {self.lines_cleared}")
        
        # Print next piece
        print(f"\nNext piece:")
        shape = self.next_tetromino.get_current_shape()
        for row in shape:
            line = ""
            for cell in row:
                if cell != '.' and cell != ' ':
                    color = COLORS.get(self.next_tetromino.color, COLORS[0])
                    line += f"{color}██{COLORS[0]}"
                else:
                    line += "  "
            print(line)
        
        # Print controls
        print(f"\nControls: a/d=move, s=drop, w=rotate, q=quit")
        
        if self.game_over:
            print(f"\n*** GAME OVER ***")

    def spawn_new_tetromino(self):
        self.current_tetromino = self.next_tetromino
        self.current_tetromino.x = 3
        self.current_tetromino.y = 0
        self.next_tetromino = Tetromino()
        
        if not self.board.is_valid_position(self.current_tetromino):
            self.game_over = True

    def lock_tetromino(self):
        self.board.place_tetromino(self.current_tetromino)
        lines_cleared = self.board.clear_lines()
        
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            score_table = {1: 40, 2: 100, 3: 300, 4: 1200}
            self.score += score_table.get(lines_cleared, 0) * self.level
            self.level = min(10, (self.lines_cleared // 10) + 1)
        
        self.spawn_new_tetromino()

    def handle_input(self, key):
        if key == 'q':
            self.running = False
            return
        
        if self.game_over:
            return
        
        if key == 'a':  # Move left
            new_tetromino = self.current_tetromino.move(-1, 0)
            if self.board.is_valid_position(new_tetromino):
                self.current_tetromino = new_tetromino
        
        elif key == 'd':  # Move right
            new_tetromino = self.current_tetromino.move(1, 0)
            if self.board.is_valid_position(new_tetromino):
                self.current_tetromino = new_tetromino
        
        elif key == 's':  # Soft drop
            new_tetromino = self.current_tetromino.move(0, 1)
            if self.board.is_valid_position(new_tetromino):
                self.current_tetromino = new_tetromino
            else:
                self.lock_tetromino()
        
        elif key == 'w':  # Rotate
            new_tetromino = self.current_tetromino.rotate_right()
            if self.board.is_valid_position(new_tetromino):
                self.current_tetromino = new_tetromino

    def run(self):
        last_fall = time.time()
        fall_speed = 1.0  # seconds
        
        print("Starting Simple Tetris...")
        print("Controls: a/d=move, s=drop, w=rotate, q=quit")
        print("Press Enter to start...")
        input()
        
        while self.running:
            # Handle input
            key = self.get_input()
            if key:
                self.handle_input(key)
            
            # Handle falling
            current_time = time.time()
            if current_time - last_fall > fall_speed and not self.game_over:
                new_tetromino = self.current_tetromino.move(0, 1)
                if self.board.is_valid_position(new_tetromino):
                    self.current_tetromino = new_tetromino
                else:
                    self.lock_tetromino()
                last_fall = current_time
            
            # Render
            self.render()
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        game = SimpleTetris()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()