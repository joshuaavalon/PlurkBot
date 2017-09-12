import json
import logging
import inspect
from plurk_api import PlurkApi
from schedule import Scheduler
from typing import Union
from threading import Thread
from time import sleep
from queue import Queue, Empty
from datetime import datetime
from utils import CatchAndLog

logging.getLogger("schedule").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class Bot(Thread):
    def __init__(self, api: PlurkApi):
        super().__init__()
        self._api = api  # type:PlurkApi
        self.scheduler = Scheduler()  # type:Scheduler
        self._register_task()
        self._is_finish = False  # type:bool

    def _register_task(self):
        pass

    @staticmethod
    def _check_error(response: Union[dict, None]) -> Union[dict, None]:
        if response is not None and "error_text" in response:
            return None
        else:
            return response

    @staticmethod
    def _log_response(response: dict, out_level: int = 1):
        name = inspect.getouterframes(inspect.currentframe())[out_level].function
        logger.info(f"function={name}, response=\n{json.dumps(response, sort_keys=True, indent=4)}")

    @staticmethod
    def _log_request(url: str, params: Union[dict, str, None] = None, out_level: int = 1):
        name = inspect.getouterframes(inspect.currentframe())[out_level].function
        if isinstance(params, dict):
            logger.info(f"function={name}, url={url}, params=\n{json.dumps(params, sort_keys=True, indent=4)}")
        else:
            logger.info(f"function={name}, url={url}, params={params}")

    def request(self, url: str, params: Union[dict, str, None] = None) -> Union[dict, None]:
        self._log_request(url, params, 2)
        response = self._api.request(url, params)
        self._log_response(response, 2)
        return self._check_error(response)

    def run(self):
        while not self._is_finish:
            self.scheduler.run_pending()
            sleep(1)

    def stop(self):
        self._is_finish = True


class Task:
    def __init__(self):
        self._bot = None  # type:TaskBot

    def start(self, bot: "TaskBot"):
        self._bot = bot
        self._task()

    def _task(self):
        pass

    def stop(self):
        pass

    def add_task(self, *tasks: "Task"):
        self._bot.add_task(*tasks)

    @CatchAndLog()
    def _add_all_friends(self, **kwargs) -> Union[dict, None]:
        return self._request("/APP/Alerts/addAllAsFriends", **kwargs)

    @CatchAndLog()
    def _get_plurk(self, plurk_id: int, **kwargs) -> Union[dict, None]:
        return self._request("/APP/Timeline/getPlurk", {"plurk_id": plurk_id, **kwargs})

    @CatchAndLog()
    def _get_responses(self, plurk_id: int, **kwargs) -> Union[dict, None]:
        return self._request("/APP/Responses/get", {"plurk_id": plurk_id, **kwargs})

    @CatchAndLog()
    def _add_response(self, plurk_id: int, content: str, qualifier: str, **kwargs) -> Union[dict, None]:
        return self._request("/APP/Responses/responseAdd",
                             {"plurk_id": plurk_id, "content": content, "qualifier": qualifier, **kwargs})

    @CatchAndLog()
    def _get_plurks(self, from_time: datetime, limit: int = 20, **kwargs) -> Union[dict, None]:
        return self._request("/APP/Polling/getPlurks", {"offset": from_time.isoformat(), "limit": limit, **kwargs})

    def _request(self, *args, **kwargs) -> Union[dict, None]:
        return self._bot.request(*args, **kwargs)


class TaskBot(Bot):
    def __init__(self, api: PlurkApi, task_queue: Queue):
        super().__init__(api)
        self._queue = task_queue  # type:Queue

    def _register_task(self):
        self.scheduler.every().second.do(self._consume_queue)

    def _consume_queue(self):
        while not self._queue.empty():
            task = None
            try:
                task = self._queue.get()
            except Empty:
                pass
            self._queue.task_done()
            if task is not None:
                task.start(self)

    def add_task(self, *tasks: Task):
        for task in tasks:
            if isinstance(task, Task):
                self._queue.put(task)
