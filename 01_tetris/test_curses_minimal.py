#!/usr/bin/env python3
"""
Minimal curses test to check if curses can initialize
"""
import curses
import sys
import os

def test_curses_init():
    """Test basic curses initialization without full wrapper"""
    try:
        # Try to initialize curses manually
        stdscr = curses.initscr()
        
        # Basic curses setup
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        
        # Check color support
        has_colors = curses.has_colors()
        print(f"Has colors: {has_colors}")
        
        if has_colors:
            curses.start_color()
            print("Color initialized")
        
        # Get screen dimensions
        height, width = stdscr.getmaxyx()
        print(f"Screen size: {width}x{height}")
        
        # Test basic drawing
        stdscr.addstr(0, 0, "Curses test - minimal")
        stdscr.refresh()
        
        print("Curses initialization successful")
        return True
        
    except Exception as e:
        print(f"Curses error: {e}")
        return False
    finally:
        try:
            curses.endwin()
        except:
            pass

def test_environment():
    """Test environment variables and terminal settings"""
    print("=== Environment Test ===")
    print(f"TERM: {os.environ.get('TERM', 'Not set')}")
    print(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    print(f"Is TTY: {sys.stdout.isatty()}")
    print(f"Is stdin TTY: {sys.stdin.isatty()}")
    
    try:
        import termios
        print("termios module available")
        # Don't try to get attributes if not a TTY
        if sys.stdin.isatty():
            termios.tcgetattr(sys.stdin)
            print("termios working")
        else:
            print("stdin is not a TTY - termios limited")
    except Exception as e:
        print(f"termios error: {e}")

if __name__ == "__main__":
    test_environment()
    print("\n=== Curses Test ===")
    test_curses_init()