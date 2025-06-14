"""Interfaces package for game components."""

from .game_interfaces import (
    IRenderer, IInputHandler, IGameBoard, ITetrominoFactory, IGameEngine,
    IScoreCalculator, IGameTimer, IAudioManager, IGamePersistence
)

__all__ = [
    'IRenderer', 'IInputHandler', 'IGameBoard', 'ITetrominoFactory', 'IGameEngine',
    'IScoreCalculator', 'IGameTimer', 'IAudioManager', 'IGamePersistence'
]