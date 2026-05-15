# =============================================================================
# File: sandbox_game/core/event_bus.py
# =============================================================================
"""
Publish-subscribe event system for decoupled cross-system communication.
"""

from typing import Dict, List, Callable, Any


class EventBus:
    """
    Centralized event system allowing systems to communicate without direct coupling.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event: str, callback: Callable) -> None:
        """
        Subscribe a callback to an event.
        
        Args:
            event: The event name to listen for
            callback: Function to call when event is published
        """
        if event not in self._subscribers:
            self._subscribers[event] = []
        
        if callback not in self._subscribers[event]:
            self._subscribers[event].append(callback)
    
    def unsubscribe(self, event: str, callback: Callable) -> None:
        """
        Unsubscribe a callback from an event.
        
        Args:
            event: The event name
            callback: The callback to remove
        """
        if event in self._subscribers and callback in self._subscribers[event]:
            self._subscribers[event].remove(callback)
    
    def publish(self, event: str, data: Any = None) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: The event name
            data: Optional data to pass to subscribers
        """
        if event in self._subscribers:
            for callback in self._subscribers[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in event handler for '{event}': {e}")


# Global event bus instance
event_bus = EventBus()
