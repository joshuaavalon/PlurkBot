import weakref
from typing import Dict, Optional

__all__ = ["EventQueue"]


class EventQueue:
    def __init__(self):
        self._subscribers = {}  # type:Dict[type,set]

    def subscribe(self, event_type: type, subscriber):
        if event_type is None:
            raise ValueError("event_type cannot be None.")
        subscribers = self._subscribers.get(event_type)  # type:Optional[set]
        if subscribers is None:
            subscribers = weakref.WeakSet()
            self._subscribers[event_type] = subscribers
        subscribers.add(subscriber)

    def unsubscribe(self, event_type: type, subscriber):
        if event_type is None:
            raise ValueError("event_type cannot be None.")
        subscribers = self._subscribers.get(event_type)  # type:Optional[set]
        try:
            subscribers.remove(subscriber)
        except (AttributeError, TypeError):
            pass

    def publish(self, event):
        for key in self._subscribers.keys():
            if not issubclass(type(event), key):
                continue
            subscribers = self._subscribers.get(key)
            if subscribers is not None:
                for subscriber in subscribers:
                    subscriber.receive(event)
