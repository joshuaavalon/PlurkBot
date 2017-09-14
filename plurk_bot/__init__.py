
from typing import List

from plurk_bot.bot import Task
from plurk_bot.factory import TaskFactory
from plurk_bot.project import ProjectBuilder
from plurk_bot.task import FriendTask, ObserverTask, ResponseTask


class TestFactory(TaskFactory):
    def create_task(self, plurk: dict):
        if plurk["qualifier"] == "loves" and plurk["no_comments"] != 1:
            return ResponseTask(plurk["plurk_id"], "Hello World!2", "loves")
        else:
            return None


def create_tasks() -> List[Task]:
    tasks = [FriendTask()]  # type:List[Task]

    observer_task = ObserverTask()
    observer_task.add_factory(TestFactory())
    tasks.append(observer_task)

    return tasks


