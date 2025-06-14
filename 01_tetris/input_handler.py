import curses
from typing import Optional


class InputHandler:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100)

    def get_input(self) -> Optional[str]:
        try:
            key = self.stdscr.getch()
            if key == -1:
                return None
            
            key_map = {
                ord('q'): 'quit',
                ord('Q'): 'quit',
                ord('p'): 'pause',
                ord('P'): 'pause',
                ord('w'): 'rotate_right',
                ord('W'): 'rotate_right',
                ord('s'): 'rotate_left',
                ord('S'): 'rotate_left',
                ord('a'): 'move_left',
                ord('A'): 'move_left',
                ord('d'): 'move_right',
                ord('D'): 'move_right',
                ord(' '): 'hard_drop',
                curses.KEY_UP: 'rotate_right',
                curses.KEY_DOWN: 'soft_drop',
                curses.KEY_LEFT: 'move_left',
                curses.KEY_RIGHT: 'move_right',
            }
            
            return key_map.get(key, None)
        except:
            return None