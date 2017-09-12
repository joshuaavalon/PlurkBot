from schedule import Job

from bot import Task, TaskBot
from datetime import datetime
from utils import CatchAndLog


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
        self.plurk_id = plurk_id  # type:int
        self.content = content  # type:str
        self.qualifier = qualifier  # type:str

    def _task(self):
        self._add_response(self.plurk_id, self.content, self.qualifier)


class PlurkTask(ScheduleTask):
    def __init__(self, refresh_limit: int = 20):
        super().__init__()
        self.refresh_limit = refresh_limit  # type:int
        self._run_period = 10
        self.last_refresh = datetime.now()  # type:datetime

    @CatchAndLog()
    def _task(self):
        check_time = datetime.now()
        response = self._get_plurks(self.last_refresh, self.refresh_limit)
        self.last_refresh = check_time
        if response is not None and "plurks" in response:
            plurks = response["plurks"]
            for plurk in plurks:
                if plurk["qualifier"] == "loves" and plurk["no_comments"] != 1:
                    self.add_task(ResponseTask(plurk["plurk_id"], "Hello World!", "loves"))
