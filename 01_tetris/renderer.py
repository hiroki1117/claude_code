import curses
from typing import List
from tetromino import Tetromino
from game_board import GameBoard


class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        curses.start_color()
        
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)     # I
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # O
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # T
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)    # S
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)      # Z
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)     # J
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)    # L
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_WHITE)    # Ghost

    def draw_board(self, board: GameBoard, current_tetromino: Tetromino = None):
        self.stdscr.clear()
        
        # Draw border
        for y in range(board.height + 2):
            self.stdscr.addstr(y, 0, '|')
            self.stdscr.addstr(y, board.width * 2 + 1, '|')
        
        for x in range(board.width * 2 + 2):
            self.stdscr.addstr(board.height + 1, x, '-')
        
        # Draw board
        board_copy = board.get_board_copy()
        
        # Draw ghost piece
        if current_tetromino:
            ghost_y = board.get_drop_position(current_tetromino)
            ghost_tetromino = current_tetromino.move(0, ghost_y - current_tetromino.y)
            ghost_blocks = ghost_tetromino.get_blocks()
            
            for x, y in ghost_blocks:
                if 0 <= y < board.height and 0 <= x < board.width:
                    if board_copy[y][x] == 0:
                        board_copy[y][x] = -1  # Ghost marker
        
        # Draw current tetromino
        if current_tetromino:
            blocks = current_tetromino.get_blocks()
            for x, y in blocks:
                if 0 <= y < board.height and 0 <= x < board.width:
                    board_copy[y][x] = current_tetromino.color
        
        # Render the board
        for y in range(board.height):
            for x in range(board.width):
                screen_x = x * 2 + 1
                screen_y = y + 1
                
                if board_copy[y][x] == -1:  # Ghost piece
                    self.stdscr.addstr(screen_y, screen_x, '[]', 
                                     curses.color_pair(8) | curses.A_DIM)
                elif board_copy[y][x] > 0:
                    self.stdscr.addstr(screen_y, screen_x, '[]', 
                                     curses.color_pair(board_copy[y][x]))
                else:
                    self.stdscr.addstr(screen_y, screen_x, '. ')

    def draw_next_piece(self, next_tetromino: Tetromino, offset_x: int = 25):
        self.stdscr.addstr(2, offset_x, "Next:")
        shape = next_tetromino.get_current_shape()
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell != '.' and cell != ' ':
                    self.stdscr.addstr(3 + row_idx, offset_x + col_idx * 2, '[]',
                                     curses.color_pair(next_tetromino.color))

    def draw_stats(self, score: int, level: int, lines: int, offset_x: int = 25):
        self.stdscr.addstr(8, offset_x, f"Score: {score}")
        self.stdscr.addstr(9, offset_x, f"Level: {level}")
        self.stdscr.addstr(10, offset_x, f"Lines: {lines}")

    def draw_controls(self, offset_x: int = 25):
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
            self.stdscr.addstr(12 + i, offset_x, control)

    def draw_game_over(self):
        height, width = self.stdscr.getmaxyx()
        message = "GAME OVER - Press Q to quit"
        self.stdscr.addstr(height // 2, (width - len(message)) // 2, message,
                          curses.A_BOLD | curses.A_BLINK)

    def draw_pause(self):
        height, width = self.stdscr.getmaxyx()
        message = "PAUSED - Press P to continue"
        self.stdscr.addstr(height // 2, (width - len(message)) // 2, message,
                          curses.A_BOLD)

    def refresh(self):
        self.stdscr.refresh()