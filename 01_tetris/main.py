#!/usr/bin/env python3
"""
Refactored main entry point using new dependency injection architecture.
"""

import curses
import sys
import os
import time
from typing import Optional

# Import new architecture components
from core import ConfigManager, Container
from interfaces.game_interfaces import (
    IGameEngine, IRenderer, IInputHandler, IGameBoard, 
    ITetrominoFactory, IScoreCalculator
)
from components import (
    TetrisGameEngine, ScoreCalculator, CursesRenderer, 
    CursesInputHandler, GameBoard, TetrominoFactory
)
from core.logger import get_logger, get_error_handler


class GameApplication:
    """Main application class with dependency injection."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.logger = get_logger()
        self.error_handler = get_error_handler()
        self.container = Container()
        self.game_engine: Optional[IGameEngine] = None
        self._running = False
    
    def setup_dependencies(self) -> None:
        """Set up dependency injection container."""
        try:
            # Register configuration manager
            config_manager = ConfigManager()
            self.container.register_instance(ConfigManager, config_manager)
            
            # Register core components
            self.container.register_singleton(IScoreCalculator, ScoreCalculator)
            self.container.register_singleton(ITetrominoFactory, TetrominoFactory)
            self.container.register_singleton(IGameBoard, GameBoard)
            
            # Register UI components with stdscr
            renderer = CursesRenderer(self.stdscr)
            input_handler = CursesInputHandler(self.stdscr)
            self.container.register_instance(IRenderer, renderer)
            self.container.register_instance(IInputHandler, input_handler)
            
            # Register game engine
            self.container.register_singleton(IGameEngine, TetrisGameEngine)
            
            # Initialize container
            self.container.initialize()
            
            self.logger.info("Dependency injection container initialized")
            
        except Exception as e:
            self.error_handler.handle_error(e, "setting up dependencies", critical=True)
            raise RuntimeError(f"Failed to setup dependencies: {e}")
    
    def run(self) -> None:
        """Run the main game loop."""
        try:
            # Setup dependencies
            self.setup_dependencies()
            
            # Get game engine
            self.game_engine = self.container.get(IGameEngine)
            input_handler = self.container.get(IInputHandler)
            
            # Start the game
            self.game_engine.start_game()
            self._running = True
            
            self.logger.info("Starting main game loop")
            
            # Main game loop
            last_time = time.time()
            
            while self._running and self.game_engine.is_running():
                try:
                    current_time = time.time()
                    delta_time = current_time - last_time
                    last_time = current_time
                    
                    # Handle input
                    input_action = input_handler.get_input(50)  # 50ms timeout
                    if input_action:
                        self.game_engine.handle_input(input_action)
                        
                        # Check for quit
                        if input_action == 'quit':
                            self._running = False
                            break
                    
                    # Update game state
                    self.game_engine.update(delta_time)
                    
                    # Small delay to prevent excessive CPU usage
                    time.sleep(0.01)
                    
                except KeyboardInterrupt:
                    self._running = False
                    break
                except Exception as e:
                    self.error_handler.handle_error(e, "main game loop")
                    # Continue running unless it's a critical error
                    if "critical" in str(e).lower():
                        break
            
            self.logger.info("Main game loop ended")
            
        except Exception as e:
            self.error_handler.handle_error(e, "running game application", critical=True)
            raise
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up application resources."""
        try:
            if self.game_engine:
                self.game_engine.cleanup()
            
            # Clean up UI components
            try:
                renderer = self.container.get(IRenderer)
                renderer.cleanup()
            except:
                pass
            
            try:
                input_handler = self.container.get(IInputHandler)
                input_handler.cleanup()
            except:
                pass
            
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.error_handler.handle_error(e, "cleaning up application")


def check_terminal_requirements() -> bool:
    """Check if terminal meets minimum requirements."""
    logger = get_logger()
    error_handler = get_error_handler()
    
    try:
        # Check if running in terminal
        if not sys.stdout.isatty():
            print("Error: Not running in a terminal")
            return False
        
        # Check terminal size
        try:
            rows, cols = os.get_terminal_size()
            min_width = 45
            min_height = 25
            
            if rows < min_height or cols < min_width:
                print(f"Error: Terminal too small ({cols}x{rows}). Need at least {min_width}x{min_height}")
                return False
                
            logger.debug(f"Terminal size: {cols}x{rows}")
            
        except Exception as e:
            error_handler.handle_error(e, "checking terminal size")
            print("Warning: Could not determine terminal size")
        
        return True
        
    except Exception as e:
        error_handler.handle_error(e, "checking terminal requirements")
        return False


def setup_curses_environment(stdscr) -> bool:
    """Set up curses environment and check capabilities."""
    logger = get_logger()
    error_handler = get_error_handler()
    
    try:
        # Basic curses setup
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        
        # Check color support
        if not curses.has_colors():
            curses.endwin()
            print("Error: Terminal does not support colors!")
            return False
        
        # Clear screen and hide cursor
        stdscr.clear()
        curses.curs_set(0)
        
        logger.debug("Curses environment setup completed")
        return True
        
    except Exception as e:
        error_handler.handle_error(e, "setting up curses environment", critical=True)
        try:
            curses.endwin()
        except:
            pass
        return False


def main_curses(stdscr):
    """Main function called by curses.wrapper."""
    logger = get_logger()
    error_handler = get_error_handler()
    
    try:
        # Set up curses environment
        if not setup_curses_environment(stdscr):
            return
        
        # Create and run application
        app = GameApplication(stdscr)
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
    except Exception as e:
        error_handler.handle_error(e, "main curses function", critical=True)
        try:
            curses.endwin()
        except:
            pass
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    logger = get_logger()
    
    try:
        logger.info("Starting Tetris game application")
        
        # Check terminal requirements
        if not check_terminal_requirements():
            sys.exit(1)
        
        # Run with curses wrapper
        curses.wrapper(main_curses)
        
        logger.info("Tetris game application ended")
        
    except Exception as e:
        print(f"Failed to initialize application: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're running in a proper terminal (not IDE)")
        print("2. Try a different terminal (Terminal.app, iTerm2, etc.)")
        print("3. Check terminal size (need at least 45x25)")
        print("4. Try: TERM=xterm-256color python3 main.py")
        print("5. Check logs in logs/ directory for more details")
        sys.exit(1)


if __name__ == "__main__":
    main()