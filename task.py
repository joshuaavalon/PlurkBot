from schedule import Job
from bot import Task, TaskBot
from datetime import datetime
from utils import CatchAndLog
from typing import List
from factory import TaskFactory


class ScheduleTask(Task):
    def __init__(self):
        super().__init__()
        self._run_period = 5  # type:int
        self._job = None  # type:Job

    def start(self, bot: TaskBot):
        self._bot = bot
        self._job = bot.scheduler.every(self._run_period).seconds.do(self._task)

    def _task(self):
        pass

    def stop(self):
        self._bot.scheduler.cancel_job(self._job)
        self._bot = None


class FriendTask(ScheduleTask):
    def _task(self):
        self._add_all_friends()


class ResponseTask(Task):
    def __init__(self, plurk_id: int, content: str, qualifier: str):
        super().__init__()
        self._plurk_id = plurk_id  # type:int
        self._content = content  # type:str
        self._qualifier = qualifier  # type:str

    def _task(self):
        self._add_response(self._plurk_id, self._content, self._qualifier)


class ObserverTask(ScheduleTask):
    def __init__(self, refresh_limit: int = 20):
        super().__init__()
        self._refresh_limit = refresh_limit  # type:int
        self._run_period = 10
        self._last_refresh = datetime.now()  # type:datetime
        self._factory_list = []  # type:List[TaskFactory]

    def add_factory(self, *args: TaskFactory):
        self._factory_list.extend(args)

    @CatchAndLog()
    def _task(self):
        check_time = datetime.now()
        response = self._get_plurks(self._last_refresh, self._refresh_limit)
        self._last_refresh = check_time
        if response is not None and "plurks" in response:
            plurks = response["plurks"]
            for plurk in plurks:
                for factory in self._factory_list:
                    tasks = factory.create_task(plurk)
                    if isinstance(tasks, list):
                        self.add_task(*tasks)
                    else:
                        self.add_task(tasks)
