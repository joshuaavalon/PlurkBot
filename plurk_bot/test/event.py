from unittest import TestCase
from plurk_bot.event import *
import gc


class FooSubscriber:
    def __init__(self):
        self.value = None

    def receive(self, event):
        self.value = event


# noinspection PyTypeChecker
class EventQueueTest(TestCase):
    def test_subscribe(self):
        queue = EventQueue()
        subscriber = FooSubscriber()
        self.assertEqual(subscriber.value, None)
        queue.publish(1)
        self.assertEqual(subscriber.value, None)
        queue.subscribe(int, subscriber)
        self.assertEqual(subscriber.value, None)
        queue.publish("")
        self.assertEqual(subscriber.value, None)
        queue.publish(1)
        self.assertEqual(subscriber.value, 1)
        queue.publish("")
        self.assertEqual(subscriber.value, 1)
        with self.assertRaises(TypeError):
            queue.subscribe(int, None)
        queue.publish(2)
        self.assertEqual(subscriber.value, 2)
        with self.assertRaises(ValueError):
            queue.subscribe(None, None)
        with self.assertRaises(ValueError):
            queue.subscribe(None, 2)
        queue.subscribe(str, FooSubscriber())
        gc.collect()
        queue.publish("")

    def test_unsubscribe(self):
        queue = EventQueue()
        subscriber = FooSubscriber()
        self.assertEqual(subscriber.value, None)
        queue.subscribe(int, subscriber)
        self.assertEqual(subscriber.value, None)
        queue.publish(1)
        self.assertEqual(subscriber.value, 1)
        queue.unsubscribe(int, subscriber)
        queue.unsubscribe(str, subscriber)
        queue.publish(2)
        self.assertEqual(subscriber.value, 1)
        queue.unsubscribe(int, None)
        with self.assertRaises(ValueError):
            queue.unsubscribe(None, None)
        with self.assertRaises(ValueError):
            queue.unsubscribe(None, 2)
