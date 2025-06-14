import random
from typing import List, Tuple


class Tetromino:
    SHAPES = {
        'I': [
            ['....', '####', '....', '....'],
            ['..#.', '..#.', '..#.', '..#.'],
            ['....', '....', '####', '....'],
            ['.#..', '.#..', '.#..', '.#..']
        ],
        'O': [
            ['##', '##']
        ],
        'T': [
            ['.#.', '###', '...'],
            ['.#.', '.##', '.#.'],
            ['...', '###', '.#.'],
            ['.#.', '##.', '.#.']
        ],
        'S': [
            ['.##', '##.', '...'],
            ['.#.', '.##', '..#']
        ],
        'Z': [
            ['##.', '.##', '...'],
            ['..#', '.##', '.#.']
        ],
        'J': [
            ['#..', '###', '...'],
            ['.##', '.#.', '.#.'],
            ['...', '###', '..#'],
            ['.#.', '.#.', '##.']
        ],
        'L': [
            ['..#', '###', '...'],
            ['.#.', '.#.', '.##'],
            ['...', '###', '#..'],
            ['##.', '.#.', '.#.']
        ]
    }
    
    COLORS = {
        'I': 1,  # Cyan
        'O': 2,  # Yellow
        'T': 3,  # Purple
        'S': 4,  # Green
        'Z': 5,  # Red
        'J': 6,  # Blue
        'L': 7   # Orange
    }

    def __init__(self, shape_type: str = None):
        if shape_type is None:
            shape_type = random.choice(list(self.SHAPES.keys()))
        
        self.shape_type = shape_type
        self.shapes = self.SHAPES[shape_type]
        self.color = self.COLORS[shape_type]
        self.rotation = 0
        self.x = 3
        self.y = 0

    def get_current_shape(self) -> List[str]:
        return self.shapes[self.rotation % len(self.shapes)]

    def rotate_right(self) -> 'Tetromino':
        new_tetromino = Tetromino(self.shape_type)
        new_tetromino.rotation = (self.rotation + 1) % len(self.shapes)
        new_tetromino.x = self.x
        new_tetromino.y = self.y
        return new_tetromino

    def rotate_left(self) -> 'Tetromino':
        new_tetromino = Tetromino(self.shape_type)
        new_tetromino.rotation = (self.rotation - 1) % len(self.shapes)
        new_tetromino.x = self.x
        new_tetromino.y = self.y
        return new_tetromino

    def move(self, dx: int, dy: int) -> 'Tetromino':
        new_tetromino = Tetromino(self.shape_type)
        new_tetromino.rotation = self.rotation
        new_tetromino.x = self.x + dx
        new_tetromino.y = self.y + dy
        return new_tetromino

    def get_blocks(self) -> List[Tuple[int, int]]:
        blocks = []
        shape = self.get_current_shape()
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell != '.' and cell != ' ':
                    blocks.append((self.x + col_idx, self.y + row_idx))
        return blocks