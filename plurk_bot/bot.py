import inspect
import json
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue
from time import sleep
from typing import Union, Optional

from plurk_api import PlurkApi
from schedule import Scheduler

from plurk_bot.event import EventQueue
from plurk_bot.utils import CatchAndLog

logging.getLogger("schedule").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

__all__ = ["Bot"]


class Bot:
    def __init__(self, api: PlurkApi, max_workers: int):
        self._thread_pool = ThreadPoolExecutor(max_workers)  # type:ThreadPoolExecutor
        self._api = api  # type:PlurkApi
        self._task_queue = Queue()  # type:Queue
        self._stop = False  # type:bool
        self.scheduler = Scheduler()  # type:Scheduler
        self._event_queue = EventQueue()  # type:EventQueue

    @staticmethod
    def _check_error(response) -> Optional[dict]:
        if isinstance(response, dict) and "error_text" not in response:
            return response
        else:
            return None

    @staticmethod
    def _log_response(url: str, response: dict):
        logger.info(f"url={url}, response=\n{json.dumps(response, sort_keys=True, indent=4)}")

    @staticmethod
    def _log_request(url: str, params: Union[dict, str, None] = None, out_level: int = 1):
        name = inspect.getouterframes(inspect.currentframe())[out_level].function
        if isinstance(params, dict):
            logger.info(f"function={name}, url={url}, params=\n{json.dumps(params, sort_keys=True, indent=4)}")
        else:
            logger.info(f"function={name}, url={url}, params={params}")

    @CatchAndLog()
    def _request(self, url: str, params: Union[dict, str, None] = None) -> Optional[dict]:
        response = self._api.request(url, params)
        self._log_response(url, response)
        return self._check_error(response)

    def request(self, url: str, params: Union[dict, str, None] = None) -> Future:
        self._log_request(url, params, 2)
        return self._thread_pool.submit(self._request, url, params)

    def stop(self):
        self._stop = True
        self._thread_pool.shutdown()

    def start(self):
        while not self._stop:
            sleep(1)
            self.scheduler.run_pending()

    def subscribe(self, *args, **kwargs):
        self._event_queue.subscribe(*args, **kwargs)

    def unsubscribe(self, *args, **kwargs):
        self._event_queue.unsubscribe(*args, **kwargs)

    def publish(self, *args, **kwargs):
        self._event_queue.publish(*args, **kwargs)
