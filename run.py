from project import ProjectBuilder
from task import FriendTask, ObserverTask, ResponseTask
import logging
import sys
from typing import List
from bot import Task
from factory import TaskFactory


class TestFactory(TaskFactory):
    def create_task(self, plurk: dict):
        if plurk["qualifier"] == "loves" and plurk["no_comments"] != 1:
            return ResponseTask(plurk["plurk_id"], "Hello World!2", "loves")
        else:
            return None


def create_tasks() -> List[Task]:
    tasks = [FriendTask()]

    observer_task = ObserverTask()
    observer_task.add_factory(TestFactory())

    return tasks


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s [%(levelname)s] <%(thread)d> %(filename)s(%(lineno)d): %(message)s",
                        level=logging.NOTSET)
    if len(sys.argv) != 5:
        logging.error(f"Invalid Parameters: {sys.argv}")
    else:
        builder = ProjectBuilder(*sys.argv[1:])
        builder.worker(4).task(*create_tasks()).build().start()
