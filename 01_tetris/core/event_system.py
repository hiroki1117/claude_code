"""Event-driven system for component communication."""

from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
import time
import weakref


class EventType(Enum):
    """Standard game event types."""
    
    # Game lifecycle events
    GAME_STARTED = "game_started"
    GAME_PAUSED = "game_paused"
    GAME_RESUMED = "game_resumed"
    GAME_OVER = "game_over"
    GAME_RESET = "game_reset"
    
    # Piece events
    PIECE_SPAWNED = "piece_spawned"
    PIECE_MOVED = "piece_moved"
    PIECE_ROTATED = "piece_rotated"
    PIECE_LOCKED = "piece_locked"
    PIECE_DROPPED = "piece_dropped"
    
    # Board events
    LINES_CLEARED = "lines_cleared"
    BOARD_UPDATED = "board_updated"
    
    # Score events
    SCORE_UPDATED = "score_updated"
    LEVEL_UP = "level_up"
    
    # Input events
    INPUT_RECEIVED = "input_received"
    
    # System events
    TIMER_TICK = "timer_tick"
    RENDER_REQUESTED = "render_requested"
    CONFIG_CHANGED = "config_changed"


@dataclass
class Event:
    """Event data structure."""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: float
    source: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


class EventHandler(ABC):
    """Abstract base class for event handlers."""
    
    @abstractmethod
    def handle_event(self, event: Event) -> None:
        """Handle a specific event."""
        pass
    
    @abstractmethod
    def get_handled_events(self) -> List[EventType]:
        """Return list of event types this handler processes."""
        pass


class EventBus:
    """Central event bus for publishing and subscribing to events."""
    
    def __init__(self):
        self._handlers: Dict[EventType, List[weakref.ReferenceType]] = {}
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        self._enabled = True
    
    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe a handler to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        # Use weak reference to prevent memory leaks
        weak_handler = weakref.ref(handler, self._cleanup_handler)
        self._handlers[event_type].append(weak_handler)
    
    def subscribe_multiple(self, handler: EventHandler) -> None:
        """Subscribe a handler to all its handled event types."""
        for event_type in handler.get_handled_events():
            self.subscribe(event_type, handler)
    
    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type not in self._handlers:
            return
        
        # Remove handler from list
        self._handlers[event_type] = [
            weak_ref for weak_ref in self._handlers[event_type]
            if weak_ref() is not handler
        ]
        
        # Clean up empty lists
        if not self._handlers[event_type]:
            del self._handlers[event_type]
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribed handlers."""
        if not self._enabled:
            return
        
        # Add to history
        self._add_to_history(event)
        
        # Get handlers for this event type
        handlers = self._handlers.get(event.event_type, [])
        
        # Clean up dead references and call active handlers
        active_handlers = []
        for weak_handler in handlers:
            handler = weak_handler()
            if handler is not None:
                active_handlers.append(weak_handler)
                try:
                    handler.handle_event(event)
                except Exception as e:
                    # Log error but don't break other handlers
                    print(f"Error handling event {event.event_type}: {e}")
        
        # Update handlers list with only active references
        if len(active_handlers) != len(handlers):
            self._handlers[event.event_type] = active_handlers
    
    def publish_event(self, event_type: EventType, data: Dict[str, Any] = None, 
                     source: str = None) -> None:
        """Convenience method to create and publish an event."""
        event = Event(
            event_type=event_type,
            data=data or {},
            timestamp=time.time(),
            source=source
        )
        self.publish(event)
    
    def get_event_history(self, event_type: Optional[EventType] = None, 
                         limit: Optional[int] = None) -> List[Event]:
        """Get event history, optionally filtered by type and limited."""
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if limit:
            events = events[-limit:]
        
        return events[:]  # Return copy
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
    
    def enable(self) -> None:
        """Enable event publishing."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable event publishing."""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """Check if event bus is enabled."""
        return self._enabled
    
    def get_handler_count(self, event_type: EventType) -> int:
        """Get number of active handlers for an event type."""
        handlers = self._handlers.get(event_type, [])
        return len([h for h in handlers if h() is not None])
    
    def get_all_event_types(self) -> List[EventType]:
        """Get all event types that have handlers."""
        return list(self._handlers.keys())
    
    def _add_to_history(self, event: Event) -> None:
        """Add event to history with size limit."""
        self._event_history.append(event)
        
        # Trim history if it exceeds maximum size
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size:]
    
    def _cleanup_handler(self, weak_ref: weakref.ReferenceType) -> None:
        """Clean up dead handler references."""
        for event_type, handlers in self._handlers.items():
            self._handlers[event_type] = [h for h in handlers if h is not weak_ref]


class CompositeEventHandler(EventHandler):
    """Event handler that delegates to multiple child handlers."""
    
    def __init__(self):
        self._child_handlers: List[EventHandler] = []
    
    def add_handler(self, handler: EventHandler) -> None:
        """Add a child handler."""
        self._child_handlers.append(handler)
    
    def remove_handler(self, handler: EventHandler) -> None:
        """Remove a child handler."""
        if handler in self._child_handlers:
            self._child_handlers.remove(handler)
    
    def handle_event(self, event: Event) -> None:
        """Delegate event to all child handlers."""
        for handler in self._child_handlers:
            if event.event_type in handler.get_handled_events():
                handler.handle_event(event)
    
    def get_handled_events(self) -> List[EventType]:
        """Return union of all child handler event types."""
        handled_events = set()
        for handler in self._child_handlers:
            handled_events.update(handler.get_handled_events())
        return list(handled_events)


class EventFilter:
    """Filter events based on various criteria."""
    
    def __init__(self):
        self._event_type_filter: Optional[List[EventType]] = None
        self._source_filter: Optional[List[str]] = None
        self._time_range: Optional[tuple] = None
    
    def filter_by_type(self, event_types: List[EventType]) -> 'EventFilter':
        """Filter by event types."""
        self._event_type_filter = event_types
        return self
    
    def filter_by_source(self, sources: List[str]) -> 'EventFilter':
        """Filter by event sources."""
        self._source_filter = sources
        return self
    
    def filter_by_time_range(self, start_time: float, end_time: float) -> 'EventFilter':
        """Filter by time range."""
        self._time_range = (start_time, end_time)
        return self
    
    def apply(self, events: List[Event]) -> List[Event]:
        """Apply filters to event list."""
        filtered_events = events
        
        if self._event_type_filter:
            filtered_events = [
                e for e in filtered_events 
                if e.event_type in self._event_type_filter
            ]
        
        if self._source_filter:
            filtered_events = [
                e for e in filtered_events 
                if e.source in self._source_filter
            ]
        
        if self._time_range:
            start_time, end_time = self._time_range
            filtered_events = [
                e for e in filtered_events 
                if start_time <= e.timestamp <= end_time
            ]
        
        return filtered_events


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def set_event_bus(event_bus: EventBus) -> None:
    """Set the global event bus instance."""
    global _global_event_bus
    _global_event_bus = event_bus