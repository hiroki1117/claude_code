#!/usr/bin/env python3
import sys
import os

print("=== Terminal Test ===")
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Is TTY: {sys.stdout.isatty()}")

try:
    rows, cols = os.get_terminal_size()
    print(f"Terminal size: {cols}x{rows}")
except Exception as e:
    print(f"Cannot get terminal size: {e}")

print(f"TERM: {os.environ.get('TERM', 'Not set')}")

try:
    import curses
    print("curses module imported successfully")
    
    def test_curses(stdscr):
        stdscr.addstr(0, 0, "Curses test successful! Press any key to exit.")
        stdscr.refresh()
        stdscr.getch()
    
    curses.wrapper(test_curses)
    print("Curses test completed successfully")
    
except Exception as e:
    print(f"Curses error: {e}")
    import traceback
    traceback.print_exc()