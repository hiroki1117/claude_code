#!/usr/bin/env python3
import curses
import sys
import os
from tetris_game import TetrisGame


def check_terminal():
    """Check if terminal is suitable for curses"""
    if not sys.stdout.isatty():
        print("Error: Not running in a terminal")
        return False
    
    # Check terminal size
    try:
        rows, cols = os.get_terminal_size()
        if rows < 25 or cols < 45:
            print(f"Error: Terminal too small ({cols}x{rows}). Need at least 45x25")
            return False
    except:
        print("Warning: Could not determine terminal size")
    
    return True


def main(stdscr):
    try:
        # Initialize curses settings
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        
        # Check if terminal supports required features
        if not curses.has_colors():
            curses.endwin()
            print("Error: Terminal does not support colors!")
            return
        
        # Clear screen and hide cursor
        stdscr.clear()
        curses.curs_set(0)
        
        # Create and run the game
        game = TetrisGame(stdscr)
        game.run()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        curses.endwin()
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if not check_terminal():
        sys.exit(1)
    
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Failed to initialize curses: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're running in a proper terminal (not IDE)")
        print("2. Try a different terminal (Terminal.app, iTerm2, etc.)")
        print("3. Check terminal size (need at least 45x25)")
        print("4. Try: TERM=xterm-256color python3 main.py")
        sys.exit(1)