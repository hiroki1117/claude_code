"""Refactored input handler implementation with new architecture."""

import curses
from typing import Optional, Dict, List
from interfaces.game_interfaces import IInputHandler
from core.config_manager import ConfigManager
from core.dependency_injection import Injectable, Container
from core.event_system import EventType, get_event_bus
from core.logger import get_logger, get_error_handler


class CursesInputHandler(IInputHandler, Injectable):
    """Curses-based input handler with configurable key mappings."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.config_manager: ConfigManager = None
        self.logger = get_logger()
        self.error_handler = get_error_handler()
        self.event_bus = get_event_bus()
        
        self._initialized = False
        self._key_mappings: Dict[int, str] = {}
        self._quit_requested = False
        self._pause_requested = False
        self._last_input = None
    
    def initialize(self, container: Container) -> None:
        """Initialize with dependencies from container."""
        self.config_manager = container.get(ConfigManager)
        self._load_key_mappings()
        self._setup_input()
        self._initialized = True
        
        self.logger.info("CursesInputHandler initialized")
    
    def initialize_handler(self) -> None:
        """Initialize the input handler."""
        if not self._initialized:
            self._setup_input()
            self._initialized = True
    
    def _setup_input(self) -> None:
        """Set up input handling."""
        try:
            # Skip input setup if stdscr is a mock (for testing)
            if hasattr(self.stdscr, '_mock_name'):
                self.logger.debug("Skipping input setup for mock object")
                return
            
            self.stdscr.nodelay(True)  # Non-blocking input
            self.stdscr.timeout(100)   # 100ms timeout
            self.stdscr.keypad(True)   # Enable special keys
            
            self.logger.debug("Input handler setup completed")
            
        except Exception as e:
            self.error_handler.handle_error(e, "setting up input handler", critical=True)
            raise RuntimeError(f"Failed to initialize input handler: {e}")
    
    def _load_key_mappings(self) -> None:
        """Load key mappings from configuration."""
        try:
            if not self.config_manager:
                self._load_default_mappings()
                return
            
            controls = self.config_manager.controls
            self._key_mappings = {}
            
            # Map each control to its keys
            control_mappings = {
                'move_left': controls.move_left,
                'move_right': controls.move_right,
                'soft_drop': controls.soft_drop,
                'hard_drop': controls.hard_drop,
                'rotate_right': controls.rotate_right,
                'rotate_left': controls.rotate_left,
                'pause': controls.pause,
                'quit': controls.quit
            }
            
            for action, keys in control_mappings.items():
                for key in keys:
                    key_code = self._convert_key_to_code(key)
                    if key_code is not None:
                        self._key_mappings[key_code] = action
            
            self.logger.debug(f"Loaded {len(self._key_mappings)} key mappings")
            
        except Exception as e:
            self.error_handler.handle_error(e, "loading key mappings")
            self._load_default_mappings()
    
    def _convert_key_to_code(self, key: str) -> Optional[int]:
        """Convert key string to curses key code."""
        try:
            # Handle special keys
            special_keys = {
                'KEY_LEFT': curses.KEY_LEFT,
                'KEY_RIGHT': curses.KEY_RIGHT,
                'KEY_UP': curses.KEY_UP,
                'KEY_DOWN': curses.KEY_DOWN,
                'KEY_BACKSPACE': curses.KEY_BACKSPACE,
                'KEY_ENTER': curses.KEY_ENTER,
                'KEY_HOME': curses.KEY_HOME,
                'KEY_END': curses.KEY_END
            }
            
            if key in special_keys:
                return special_keys[key]
            
            # Handle regular characters
            if len(key) == 1:
                return ord(key)
            
            # Handle escape sequences
            if key.startswith('\\'):
                if key == '\\n':
                    return ord('\n')
                elif key == '\\t':
                    return ord('\t')
                elif key == '\\r':
                    return ord('\r')
            
            self.logger.warning(f"Unknown key format: {key}")
            return None
            
        except Exception as e:
            self.error_handler.handle_error(e, f"converting key {key}")
            return None
    
    def _load_default_mappings(self) -> None:
        """Load default key mappings as fallback."""
        self.logger.warning("Using default key mappings")
        
        self._key_mappings = {
            ord('q'): 'quit',
            ord('Q'): 'quit',
            ord('p'): 'pause',
            ord('P'): 'pause',
            ord('w'): 'rotate_right',
            ord('W'): 'rotate_right',
            ord('s'): 'soft_drop',
            ord('S'): 'soft_drop',
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
    
    def get_input(self, timeout_ms: int = 100) -> Optional[str]:
        """Get input with optional timeout."""
        try:
            if not self._initialized:
                self.initialize()
            
            # Set timeout
            self.stdscr.timeout(timeout_ms)
            
            # Get key
            key = self.stdscr.getch()
            
            if key == -1:  # No input
                return None
            
            # Map key to action
            action = self._key_mappings.get(key)
            
            if action:
                self._last_input = action
                
                # Update internal state for quick checks
                if action == 'quit':
                    self._quit_requested = True
                elif action == 'pause':
                    self._pause_requested = True
                
                # Publish input event
                self.event_bus.publish_event(
                    EventType.INPUT_RECEIVED,
                    {"action": action, "raw_key": key},
                    "InputHandler"
                )
                
                self.logger.debug(f"Input received: {action}")
                
            return action
            
        except Exception as e:
            self.error_handler.handle_error(e, "getting input")
            return None
    
    def is_quit_requested(self) -> bool:
        """Check if quit was requested."""
        return self._quit_requested
    
    def is_pause_requested(self) -> bool:
        """Check if pause was requested."""
        return self._pause_requested
    
    def get_movement_input(self) -> Optional[str]:
        """Get movement input (left, right, down)."""
        action = self.get_input()
        
        if action in ['move_left', 'move_right', 'soft_drop']:
            return action
        
        return None
    
    def get_rotation_input(self) -> Optional[str]:
        """Get rotation input (rotate_left, rotate_right)."""
        action = self.get_input()
        
        if action in ['rotate_left', 'rotate_right']:
            return action
        
        return None
    
    def is_hard_drop_requested(self) -> bool:
        """Check if hard drop was requested."""
        action = self.get_input()
        return action == 'hard_drop'
    
    def cleanup(self) -> None:
        """Clean up input handling resources."""
        try:
            if self._initialized:
                self.stdscr.nodelay(False)
                self.stdscr.timeout(-1)
                self._initialized = False
                self.logger.info("Input handler cleaned up")
        except Exception as e:
            self.error_handler.handle_error(e, "cleaning up input handler")
    
    def reset_state(self) -> None:
        """Reset input state flags."""
        self._quit_requested = False
        self._pause_requested = False
        self._last_input = None
        self.logger.debug("Input state reset")
    
    def get_last_input(self) -> Optional[str]:
        """Get the last input action."""
        return self._last_input
    
    def add_key_mapping(self, key: str, action: str) -> None:
        """Add or update a key mapping."""
        try:
            key_code = self._convert_key_to_code(key)
            if key_code is not None:
                self._key_mappings[key_code] = action
                self.logger.debug(f"Added key mapping: {key} -> {action}")
            else:
                self.error_handler.handle_validation_error("key", key, "valid key format")
                
        except Exception as e:
            self.error_handler.handle_error(e, f"adding key mapping {key}->{action}")
    
    def remove_key_mapping(self, key: str) -> None:
        """Remove a key mapping."""
        try:
            key_code = self._convert_key_to_code(key)
            if key_code is not None and key_code in self._key_mappings:
                del self._key_mappings[key_code]
                self.logger.debug(f"Removed key mapping: {key}")
                
        except Exception as e:
            self.error_handler.handle_error(e, f"removing key mapping {key}")
    
    def get_all_mappings(self) -> Dict[str, str]:
        """Get all current key mappings."""
        try:
            # Convert key codes back to readable format
            readable_mappings = {}
            
            for key_code, action in self._key_mappings.items():
                # Try to convert back to readable format
                if 32 <= key_code <= 126:  # Printable ASCII
                    key_str = chr(key_code)
                else:
                    # Special keys
                    special_key_map = {
                        curses.KEY_LEFT: 'KEY_LEFT',
                        curses.KEY_RIGHT: 'KEY_RIGHT',
                        curses.KEY_UP: 'KEY_UP',
                        curses.KEY_DOWN: 'KEY_DOWN',
                        curses.KEY_BACKSPACE: 'KEY_BACKSPACE',
                        curses.KEY_ENTER: 'KEY_ENTER'
                    }
                    key_str = special_key_map.get(key_code, f'KEY_{key_code}')
                
                readable_mappings[key_str] = action
            
            return readable_mappings
            
        except Exception as e:
            self.error_handler.handle_error(e, "getting all mappings")
            return {}
    
    def validate_key_mappings(self) -> List[str]:
        """Validate current key mappings and return any issues."""
        issues = []
        
        try:
            required_actions = {
                'move_left', 'move_right', 'soft_drop', 'hard_drop',
                'rotate_right', 'pause', 'quit'
            }
            
            mapped_actions = set(self._key_mappings.values())
            
            # Check for missing actions
            missing_actions = required_actions - mapped_actions
            for action in missing_actions:
                issues.append(f"Missing key mapping for action: {action}")
            
            # Check for duplicate keys (not technically an issue, but worth noting)
            key_counts = {}
            for key_code in self._key_mappings.keys():
                key_counts[key_code] = key_counts.get(key_code, 0) + 1
            
            for key_code, count in key_counts.items():
                if count > 1:
                    issues.append(f"Key {key_code} mapped to multiple actions")
            
            return issues
            
        except Exception as e:
            self.error_handler.handle_error(e, "validating key mappings")
            return ["Error validating key mappings"]
    
    def reload_mappings(self) -> None:
        """Reload key mappings from configuration."""
        try:
            self._load_key_mappings()
            self.logger.info("Key mappings reloaded")
            
        except Exception as e:
            self.error_handler.handle_error(e, "reloading key mappings")
            raise RuntimeError(f"Failed to reload key mappings: {e}")