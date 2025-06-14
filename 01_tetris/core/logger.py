"""Comprehensive logging system for Tetris game."""

import logging
import sys
import os
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime
import json


class LogLevel(Enum):
    """Log levels enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    """Centralized logging system with multiple output formats."""
    
    def __init__(self, name: str = "tetris", log_level: LogLevel = LogLevel.INFO):
        self.name = name
        self.log_level = log_level
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, log_level.value))
        
        # Prevent duplicate handlers
        if not self._logger.handlers:
            self._setup_handlers()
        
        self._context: Dict[str, Any] = {}
    
    def _setup_handlers(self) -> None:
        """Set up logging handlers."""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # File handler
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, f"{self.name}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Error file handler
        error_file = os.path.join(log_dir, f"{self.name}_errors.log")
        error_handler = logging.FileHandler(error_file)
        error_handler.setLevel(logging.ERROR)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter('%(levelname)s: %(message)s')
        
        console_handler.setFormatter(simple_formatter)
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)
        self._logger.addHandler(error_handler)
    
    def set_context(self, **context) -> None:
        """Set logging context information."""
        self._context.update(context)
    
    def clear_context(self) -> None:
        """Clear logging context."""
        self._context.clear()
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self._log(LogLevel.ERROR, message, exc_info=True, **kwargs)
    
    def _log(self, level: LogLevel, message: str, **kwargs) -> None:
        """Internal logging method."""
        # Combine context with additional data
        log_data = {**self._context, **kwargs}
        
        # Format message with context if available
        if log_data:
            extra_info = " | ".join(f"{k}={v}" for k, v in log_data.items() if k != 'exc_info')
            if extra_info:
                message = f"{message} | {extra_info}"
        
        # Log at appropriate level
        log_method = getattr(self._logger, level.value.lower())
        log_method(message, exc_info=kwargs.get('exc_info', False))


class GameLogger:
    """Specialized logger for game events and metrics."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self._game_session_id: Optional[str] = None
        self._metrics: Dict[str, Any] = {}
    
    def start_game_session(self, session_id: str) -> None:
        """Start a new game session."""
        self._game_session_id = session_id
        self._metrics = {
            'start_time': datetime.now().isoformat(),
            'pieces_spawned': 0,
            'lines_cleared': 0,
            'moves_made': 0,
            'rotations_made': 0,
            'drops_made': 0
        }
        
        self.logger.set_context(session_id=session_id)
        self.logger.info("Game session started")
    
    def end_game_session(self, final_score: int, final_level: int) -> None:
        """End the current game session."""
        if not self._game_session_id:
            return
        
        self._metrics.update({
            'end_time': datetime.now().isoformat(),
            'final_score': final_score,
            'final_level': final_level
        })
        
        self.logger.info("Game session ended", **self._metrics)
        self._save_session_metrics()
        
        self._game_session_id = None
        self._metrics = {}
        self.logger.clear_context()
    
    def log_piece_spawned(self, piece_type: str) -> None:
        """Log piece spawn event."""
        self._metrics['pieces_spawned'] += 1
        self.logger.debug(f"Piece spawned: {piece_type}", 
                         piece_type=piece_type, 
                         total_pieces=self._metrics['pieces_spawned'])
    
    def log_piece_moved(self, direction: str) -> None:
        """Log piece movement."""
        self._metrics['moves_made'] += 1
        self.logger.debug(f"Piece moved: {direction}", 
                         direction=direction,
                         total_moves=self._metrics['moves_made'])
    
    def log_piece_rotated(self, direction: str) -> None:
        """Log piece rotation."""
        self._metrics['rotations_made'] += 1
        self.logger.debug(f"Piece rotated: {direction}",
                         direction=direction,
                         total_rotations=self._metrics['rotations_made'])
    
    def log_piece_dropped(self, drop_type: str) -> None:
        """Log piece drop."""
        self._metrics['drops_made'] += 1
        self.logger.debug(f"Piece dropped: {drop_type}",
                         drop_type=drop_type,
                         total_drops=self._metrics['drops_made'])
    
    def log_lines_cleared(self, count: int, score_gained: int) -> None:
        """Log line clearing event."""
        self._metrics['lines_cleared'] += count
        self.logger.info(f"Lines cleared: {count}",
                        lines_cleared=count,
                        score_gained=score_gained,
                        total_lines=self._metrics['lines_cleared'])
    
    def log_level_up(self, new_level: int) -> None:
        """Log level up event."""
        self.logger.info(f"Level up: {new_level}", new_level=new_level)
    
    def log_game_over(self, reason: str) -> None:
        """Log game over event."""
        self.logger.info(f"Game over: {reason}", reason=reason)
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log game error with context."""
        self.logger.error(f"Game error in {context}: {error}", 
                         error_type=type(error).__name__,
                         context=context)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "") -> None:
        """Log performance metric."""
        self.logger.debug(f"Performance: {metric_name} = {value} {unit}",
                         metric=metric_name,
                         value=value,
                         unit=unit)
    
    def _save_session_metrics(self) -> None:
        """Save session metrics to file."""
        if not self._game_session_id or not self._metrics:
            return
        
        metrics_dir = "logs/metrics"
        if not os.path.exists(metrics_dir):
            os.makedirs(metrics_dir)
        
        metrics_file = os.path.join(metrics_dir, f"session_{self._game_session_id}.json")
        
        try:
            with open(metrics_file, 'w') as f:
                json.dump(self._metrics, f, indent=2)
        except IOError as e:
            self.logger.error(f"Failed to save session metrics: {e}")


class ErrorHandler:
    """Centralized error handling system."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self._error_counts: Dict[str, int] = {}
    
    def handle_error(self, error: Exception, context: str = "", 
                    critical: bool = False) -> None:
        """Handle and log errors with context."""
        error_type = type(error).__name__
        self._error_counts[error_type] = self._error_counts.get(error_type, 0) + 1
        
        if critical:
            self.logger.critical(f"Critical error in {context}: {error}",
                               error_type=error_type,
                               context=context,
                               count=self._error_counts[error_type])
        else:
            self.logger.error(f"Error in {context}: {error}",
                            error_type=error_type,
                            context=context,
                            count=self._error_counts[error_type])
    
    def handle_validation_error(self, field: str, value: Any, 
                              expected: str) -> None:
        """Handle validation errors."""
        self.logger.warning(f"Validation error: {field} = {value}, expected {expected}",
                          field=field,
                          value=value,
                          expected=expected)
    
    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics."""
        return self._error_counts.copy()


# Global logger instances
_global_logger: Optional[Logger] = None
_global_game_logger: Optional[GameLogger] = None
_global_error_handler: Optional[ErrorHandler] = None


def get_logger(name: str = "tetris") -> Logger:
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger(name)
    return _global_logger


def get_game_logger() -> GameLogger:
    """Get or create global game logger instance."""
    global _global_game_logger
    if _global_game_logger is None:
        _global_game_logger = GameLogger(get_logger())
    return _global_game_logger


def get_error_handler() -> ErrorHandler:
    """Get or create global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler(get_logger())
    return _global_error_handler