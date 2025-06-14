from typing import List, Tuple, Optional
from tetromino import Tetromino


class GameBoard:
    def __init__(self, width: int = 10, height: int = 20):
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(width)] for _ in range(height)]

    def is_valid_position(self, tetromino: Tetromino) -> bool:
        blocks = tetromino.get_blocks()
        for x, y in blocks:
            if x < 0 or x >= self.width or y >= self.height:
                return False
            if y >= 0 and self.board[y][x] != 0:
                return False
        return True

    def place_tetromino(self, tetromino: Tetromino) -> None:
        blocks = tetromino.get_blocks()
        for x, y in blocks:
            if 0 <= y < self.height and 0 <= x < self.width:
                self.board[y][x] = tetromino.color

    def clear_lines(self) -> int:
        lines_cleared = 0
        y = self.height - 1
        
        while y >= 0:
            if all(self.board[y][x] != 0 for x in range(self.width)):
                del self.board[y]
                self.board.insert(0, [0 for _ in range(self.width)])
                lines_cleared += 1
            else:
                y -= 1
        
        return lines_cleared

    def is_game_over(self) -> bool:
        return any(self.board[0][x] != 0 for x in range(self.width))

    def get_drop_position(self, tetromino: Tetromino) -> int:
        drop_y = tetromino.y
        while True:
            test_tetromino = tetromino.move(0, drop_y - tetromino.y + 1)
            if not self.is_valid_position(test_tetromino):
                break
            drop_y += 1
        return drop_y

    def get_board_copy(self) -> List[List[int]]:
        return [row[:] for row in self.board]