import time
import random
from tetromino import Tetromino
from game_board import GameBoard
from input_handler import InputHandler
from renderer import Renderer


class TetrisGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.board = GameBoard()
        self.input_handler = InputHandler(stdscr)
        self.renderer = Renderer(stdscr)
        
        self.current_tetromino = Tetromino()
        self.next_tetromino = Tetromino()
        
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        
        self.lock_delay = 500  # milliseconds - time to allow movement after landing  
        self.lock_timer = 0
        self.is_grounded = False
        self.move_resets = 0
        self.max_move_resets = 15  # Maximum number of moves/rotations allowed on ground
        
        self.game_over = False
        self.paused = False
        
        self.last_update_time = time.time() * 1000

    def calculate_fall_speed(self) -> int:
        return max(50, 500 - (self.level - 1) * 50)

    def calculate_score(self, lines_cleared: int) -> int:
        score_table = {0: 0, 1: 40, 2: 100, 3: 300, 4: 1200}
        return score_table.get(lines_cleared, 0) * self.level

    def spawn_new_tetromino(self):
        self.current_tetromino = self.next_tetromino
        self.current_tetromino.x = 3
        self.current_tetromino.y = 0
        self.next_tetromino = Tetromino()
        
        # Reset lock delay state
        self.is_grounded = False
        self.lock_timer = 0
        self.move_resets = 0
        
        if not self.board.is_valid_position(self.current_tetromino):
            self.game_over = True

    def handle_input(self):
        action = self.input_handler.get_input()
        if action is None:
            return True

        if action == 'quit':
            return False
        elif action == 'pause':
            self.paused = not self.paused
            return True

        if self.paused or self.game_over:
            return True

        if action == 'move_left':
            new_tetromino = self.current_tetromino.move(-1, 0)
            if self.board.is_valid_position(new_tetromino):
                self.current_tetromino = new_tetromino
                self.reset_lock_delay()

        elif action == 'move_right':
            new_tetromino = self.current_tetromino.move(1, 0)
            if self.board.is_valid_position(new_tetromino):
                self.current_tetromino = new_tetromino
                self.reset_lock_delay()

        elif action == 'soft_drop':
            new_tetromino = self.current_tetromino.move(0, 1)
            if self.board.is_valid_position(new_tetromino):
                self.current_tetromino = new_tetromino

        elif action == 'hard_drop':
            drop_y = self.board.get_drop_position(self.current_tetromino)
            self.current_tetromino = self.current_tetromino.move(0, drop_y - self.current_tetromino.y)
            self.lock_tetromino()

        elif action == 'rotate_right':
            new_tetromino = self.current_tetromino.rotate_right()
            if self.board.is_valid_position(new_tetromino):
                self.current_tetromino = new_tetromino
                self.reset_lock_delay()

        elif action == 'rotate_left':
            new_tetromino = self.current_tetromino.rotate_left()
            if self.board.is_valid_position(new_tetromino):
                self.current_tetromino = new_tetromino
                self.reset_lock_delay()

        return True

    def reset_lock_delay(self):
        if self.is_grounded and self.move_resets < self.max_move_resets:
            self.lock_timer = 0
            self.move_resets += 1

    def lock_tetromino(self):
        self.board.place_tetromino(self.current_tetromino)
        lines_cleared = self.board.clear_lines()
        
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            self.score += self.calculate_score(lines_cleared)
            self.level = min(10, (self.lines_cleared // 10) + 1)
            self.fall_speed = self.calculate_fall_speed()
        
        self.spawn_new_tetromino()

    def update_game_state(self):
        if self.paused or self.game_over:
            return

        current_time = time.time() * 1000
        time_delta = current_time - self.last_update_time
        self.fall_time += time_delta
        self.last_update_time = current_time

        # Check if tetromino is grounded
        new_tetromino = self.current_tetromino.move(0, 1)
        if not self.board.is_valid_position(new_tetromino):
            # Tetromino is grounded
            if not self.is_grounded:
                # First time grounded, start lock delay
                self.is_grounded = True
                self.lock_timer = 0
                self.move_resets = 0
            
            self.lock_timer += time_delta
            
            # Check if lock delay has expired
            if self.lock_timer >= self.lock_delay:
                self.lock_tetromino()
                return
        else:
            # Tetromino is not grounded, reset grounded state
            self.is_grounded = False
            self.lock_timer = 0
            self.move_resets = 0

        # Handle normal falling
        if self.fall_time >= self.fall_speed:
            if self.board.is_valid_position(new_tetromino):
                self.current_tetromino = new_tetromino
            
            self.fall_time = 0

    def render(self):
        self.renderer.draw_board(self.board, self.current_tetromino)
        self.renderer.draw_next_piece(self.next_tetromino)
        self.renderer.draw_stats(self.score, self.level, self.lines_cleared)
        self.renderer.draw_controls()
        
        if self.game_over:
            self.renderer.draw_game_over()
        elif self.paused:
            self.renderer.draw_pause()
        
        self.renderer.refresh()

    def run(self):
        while True:
            if not self.handle_input():
                break
            
            self.update_game_state()
            self.render()
            
            if self.game_over and self.input_handler.get_input() == 'quit':
                break
            
            time.sleep(0.01)  # Small delay to prevent high CPU usage