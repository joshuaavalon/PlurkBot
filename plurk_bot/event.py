from typing import Optional, Callable, Set
import logging

__all__ = ["EventQueue"]


class EventQueue:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type: type, subscriber: Callable):
        if event_type is None:
            raise ValueError("event_type cannot be None.")
        if subscriber is None:
            raise TypeError("subscriber cannot be None.")
        subscribers = self._subscribers.get(event_type)  # type:Optional[Set[Callable]]
        if subscribers is None:
            subscribers = set()
            self._subscribers[event_type] = subscribers
        subscribers.add(subscriber)

    def unsubscribe(self, event_type: type, subscriber):
        if event_type is None:
            raise ValueError("event_type cannot be None.")
        subscribers = self._subscribers.get(event_type)  # type:Optional[Set[Callable]]
        try:
            subscribers.remove(subscriber)
        except (AttributeError, KeyError):
            pass

    def publish(self, event):
        for key in self._subscribers.keys():
            if not issubclass(type(event), key):
                continue
            subscribers = self._subscribers.get(key)
            for subscriber in subscribers.copy():
                try:
                    subscriber(event)
                except TypeError as e:
                    logging.error(e)
                    self.unsubscribe(key, subscriber)
