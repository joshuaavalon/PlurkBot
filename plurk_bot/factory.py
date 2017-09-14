from typing import List, Union

from plurk_bot.bot import Task


class TaskFactory:
    def create_task(self, plurk: dict) -> Union[Task, List[Task], None]:
        return None
