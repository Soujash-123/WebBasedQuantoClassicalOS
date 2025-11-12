"""
Event Bus
Lightweight internal message bus for inter-module communication.
"""

from typing import Callable, Dict, List, Any
from collections import defaultdict


class EventBus:
    """Synchronous event bus for inter-module communication."""
    
    def __init__(self):
        """Initialize the Event Bus."""
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        print("[EventBus] Event Bus initialized")
    
    def subscribe(self, event_name: str, callback: Callable) -> bool:
        """
        Subscribe to an event.
        
        Args:
            event_name: Name of the event to subscribe to
            callback: Function to call when event is published
            
        Returns:
            True if subscription successful
        """
        if callback in self.subscribers[event_name]:
            print(f"[EventBus] Warning: Callback already subscribed to '{event_name}'")
            return False
        
        self.subscribers[event_name].append(callback)
        print(f"[EventBus] Subscribed to event '{event_name}'")
        return True
    
    def unsubscribe(self, event_name: str, callback: Callable) -> bool:
        """
        Unsubscribe from an event.
        
        Args:
            event_name: Name of the event to unsubscribe from
            callback: Function to remove from subscribers
            
        Returns:
            True if unsubscription successful, False if callback not found
        """
        if event_name not in self.subscribers:
            print(f"[EventBus] Warning: No subscribers for event '{event_name}'")
            return False
        
        if callback not in self.subscribers[event_name]:
            print(f"[EventBus] Warning: Callback not found for event '{event_name}'")
            return False
        
        self.subscribers[event_name].remove(callback)
        print(f"[EventBus] Unsubscribed from event '{event_name}'")
        
        # Clean up empty subscriber lists
        if not self.subscribers[event_name]:
            del self.subscribers[event_name]
        
        return True
    
    def publish(self, event_name: str, data: Any = None) -> int:
        """
        Publish an event to all subscribers.
        
        Args:
            event_name: Name of the event to publish
            data: Optional data to pass to subscribers
            
        Returns:
            Number of subscribers notified
        """
        if event_name not in self.subscribers:
            print(f"[EventBus] Event '{event_name}' published (no subscribers)")
            return 0
        
        subscriber_count = len(self.subscribers[event_name])
        print(f"[EventBus] Publishing event '{event_name}' to {subscriber_count} subscriber(s)")
        
        for callback in self.subscribers[event_name]:
            try:
                callback(data)
            except Exception as e:
                print(f"[EventBus] Error in callback for event '{event_name}': {e}")
        
        return subscriber_count
    
    def get_subscribers(self, event_name: str) -> int:
        """
        Get the number of subscribers for an event.
        
        Args:
            event_name: Name of the event
            
        Returns:
            Number of subscribers
        """
        return len(self.subscribers.get(event_name, []))
    
    def list_events(self) -> List[str]:
        """
        Get list of all events with subscribers.
        
        Returns:
            List of event names
        """
        return list(self.subscribers.keys())
    
    def clear_event(self, event_name: str) -> bool:
        """
        Clear all subscribers for a specific event.
        
        Args:
            event_name: Name of the event to clear
            
        Returns:
            True if event was cleared, False if event didn't exist
        """
        if event_name in self.subscribers:
            count = len(self.subscribers[event_name])
            del self.subscribers[event_name]
            print(f"[EventBus] Cleared {count} subscriber(s) for event '{event_name}'")
            return True
        return False
    
    def clear_all(self) -> None:
        """Clear all event subscriptions."""
        event_count = len(self.subscribers)
        self.subscribers.clear()
        print(f"[EventBus] All subscriptions cleared. {event_count} event(s) removed")
