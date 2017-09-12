from queue import Queue
from typing import List
from plurk_api import PlurkApi

from bot import Bot, Task, TaskBot


class Project:
    def __init__(self, bots: List[Bot], queue: Queue):
        self._bots = bots  # type:List[Bot]
        self._queue = queue  # type:Queue

    def start(self):
        for bot in self._bots:
            bot.run()

    def stop(self):
        for bot in self._bots:
            bot.stop()


class ProjectBuilder:
    def __init__(self, api_key: str, api_secret: str, token_key: str, token_secret: str):
        self._api = PlurkApi(api_key, api_secret, token_key, token_secret)  # type:PlurkApi
        self._workers_count = 3
        self._queue = Queue()

    def worker(self, count: int) -> "ProjectBuilder":
        self._workers_count = count
        return self

    def task(self, *tasks: Task) -> "ProjectBuilder":
        for task in tasks:
            if isinstance(task, Task):
                self._queue.put(task)
        return self

    def build(self) -> Project:
        bots = []
        for _ in range(self._workers_count):
            bots.append(TaskBot(self._api, self._queue))
        project = Project(bots, self._queue)
        self._queue = Queue()
        return project
