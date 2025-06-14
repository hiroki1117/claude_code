"""Configuration management system for Tetris game."""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class GameConfig:
    """Game configuration settings."""
    board_width: int = 10
    board_height: int = 20
    initial_fall_speed: int = 500
    fall_speed_increment: int = 50
    min_fall_speed: int = 50
    lock_delay: int = 500
    max_move_resets: int = 15
    lines_per_level: int = 10


@dataclass
class ScoringConfig:
    """Scoring system configuration."""
    single_line: int = 40
    double_line: int = 100
    triple_line: int = 300
    tetris: int = 1200


@dataclass
class DisplayConfig:
    """Display configuration settings."""
    terminal_min_width: int = 45
    terminal_min_height: int = 25
    board_offset_x: int = 2
    board_offset_y: int = 2
    info_offset_x: int = 25
    colors: Dict[str, int] = None

    def __post_init__(self):
        if self.colors is None:
            self.colors = {
                "I": 6, "O": 3, "T": 5, "S": 2, "Z": 1, "J": 4, "L": 7,
                "ghost": 8, "board": 9
            }


@dataclass
class ControlsConfig:
    """Controls configuration."""
    move_left: List[str] = None
    move_right: List[str] = None
    soft_drop: List[str] = None
    hard_drop: List[str] = None
    rotate_right: List[str] = None
    rotate_left: List[str] = None
    pause: List[str] = None
    quit: List[str] = None

    def __post_init__(self):
        if self.move_left is None:
            self.move_left = ["a", "KEY_LEFT"]
        if self.move_right is None:
            self.move_right = ["d", "KEY_RIGHT"]
        if self.soft_drop is None:
            self.soft_drop = ["s", "KEY_DOWN"]
        if self.hard_drop is None:
            self.hard_drop = [" "]
        if self.rotate_right is None:
            self.rotate_right = ["w", "KEY_UP"]
        if self.rotate_left is None:
            self.rotate_left = ["q"]
        if self.pause is None:
            self.pause = ["p"]
        if self.quit is None:
            self.quit = ["Q"]


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self._config_data: Dict[str, Any] = {}
        self._game_config: Optional[GameConfig] = None
        self._scoring_config: Optional[ScoringConfig] = None
        self._display_config: Optional[DisplayConfig] = None
        self._controls_config: Optional[ControlsConfig] = None
        
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config_data = json.load(f)
            else:
                self._config_data = {}
                self.save_config()  # Create default config file
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    @property
    def game(self) -> GameConfig:
        """Get game configuration."""
        if self._game_config is None:
            game_data = self._config_data.get('game', {})
            self._game_config = GameConfig(**game_data)
        return self._game_config
    
    @property
    def scoring(self) -> ScoringConfig:
        """Get scoring configuration."""
        if self._scoring_config is None:
            scoring_data = self._config_data.get('scoring', {})
            self._scoring_config = ScoringConfig(**scoring_data)
        return self._scoring_config
    
    @property
    def display(self) -> DisplayConfig:
        """Get display configuration."""
        if self._display_config is None:
            display_data = self._config_data.get('display', {})
            self._display_config = DisplayConfig(**display_data)
        return self._display_config
    
    @property
    def controls(self) -> ControlsConfig:
        """Get controls configuration."""
        if self._controls_config is None:
            controls_data = self._config_data.get('controls', {})
            self._controls_config = ControlsConfig(**controls_data)
        return self._controls_config
    
    def get_tetromino_config(self, piece_type: str) -> Dict[str, Any]:
        """Get tetromino configuration for specific piece type."""
        tetrominoes = self._config_data.get('tetrominoes', {})
        if piece_type not in tetrominoes:
            raise ConfigurationError(f"Unknown tetromino type: {piece_type}")
        return tetrominoes[piece_type]
    
    def get_all_tetromino_types(self) -> List[str]:
        """Get list of all available tetromino types."""
        return list(self._config_data.get('tetrominoes', {}).keys())
    
    def update_config(self, section: str, data: Dict[str, Any]) -> None:
        """Update configuration section."""
        self._config_data[section] = data
        self._invalidate_cache()
        self.save_config()
    
    def _invalidate_cache(self) -> None:
        """Invalidate cached configuration objects."""
        self._game_config = None
        self._scoring_config = None
        self._display_config = None
        self._controls_config = None


class ConfigurationError(Exception):
    """Raised when configuration operations fail."""
    pass