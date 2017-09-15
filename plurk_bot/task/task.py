import logging
from concurrent.futures import Future, wait
from datetime import datetime
from typing import List, Callable, Union

from schedule import Scheduler, Job

from plurk_bot.bot import Bot
from plurk_bot.task.event import NewPlurkEvent
from plurk_bot.utils import CatchAndLog

__all__ = ["Task", "TimeLineListenerTask", "FriendTask", "ResponseTask", "Response", "simple_response",
           "get_public_profiles"]
logger = logging.getLogger(__name__)


class Task:
    def __init__(self, bot: Bot):
        self._bot = bot  # type:Bot
        self._scheduler = self._bot.scheduler  # type:Scheduler

    def _publish(self, event):
        self._bot.publish(event)

    @CatchAndLog()
    def _add_all_friends(self, **kwargs) -> Future:
        return self._request("/APP/Alerts/addAllAsFriends", **kwargs)

    @CatchAndLog()
    def _get_plurk(self, plurk_id: int, **kwargs) -> Future:
        return self._request("/APP/Timeline/getPlurk", {"plurk_id": plurk_id, **kwargs})

    @CatchAndLog()
    def _get_responses(self, plurk_id: int, **kwargs) -> Future:
        return self._request("/APP/Responses/get", {"plurk_id": plurk_id, **kwargs})

    @CatchAndLog()
    def _add_response(self, plurk_id: int, content: str, qualifier: str, **kwargs) -> Future:
        return self._request("/APP/Responses/responseAdd",
                             {"plurk_id": plurk_id, "content": content, "qualifier": qualifier, **kwargs})

    @CatchAndLog()
    def _get_plurks(self, from_time: datetime, limit: int = 20, **kwargs) -> Future:
        return self._request("/APP/Polling/getPlurks", {"offset": from_time.isoformat(), "limit": limit, **kwargs})

    @CatchAndLog()
    def _get_public_profile(self, user_id: Union[int, str], **kwargs) -> Future:
        return self._request("/APP/Profile/getPublicProfile", {"user_id": user_id, **kwargs})

    def _request(self, *args, **kwargs) -> Future:
        return self._bot.request(*args, **kwargs)


class TimeLineListenerTask(Task):
    def __init__(self, bot: Bot, refresh_limit: int = 20, period: int = 10):
        super().__init__(bot)
        self._refresh_limit = refresh_limit  # type:int
        self._last_refresh = datetime.utcnow()  # type:datetime
        self._scheduler.every(period).seconds.do(self._task)

    def _task(self):
        check_time = datetime.utcnow()
        future = self._get_plurks(self._last_refresh, self._refresh_limit)
        self._last_refresh = check_time
        future.add_done_callback(self._result)

    def _result(self, future: Future):
        response = future.result()
        try:
            plurks = response["plurks"]  # type:List[dict]
        except (TypeError, AttributeError, KeyError) as e:
            logger.error(f"error={e}, response={response}")
        else:
            if isinstance(plurks, list) and len(plurks) > 0:
                self._publish(NewPlurkEvent(plurks))


class FriendTask(Task):
    def __init__(self, bot: Bot, period: int = 60):
        super().__init__(bot)
        self._scheduler.every(period).seconds.do(self._task)

    def _task(self):
        self._add_all_friends()


class ResponseTask(Task):
    def __init__(self, bot: Bot, responses: List["Response"], period: int = 60, retry: int = 3):
        super().__init__(bot)
        self._responses = self._split_response(responses)  # type:List[Response]
        self._retry = retry  # type:int
        self._job = self._scheduler.every(period).seconds.do(self._response).run()

    @staticmethod
    def _split_response(responses: List["Response"]) -> List["Response"]:
        new_responses = []
        step = 360
        for response in responses:
            for i in range(0, len(response.content), step):
                new_responses.append(response.content[i:i + step])
        return new_responses

    def _response(self):
        if len(self._responses) <= 0:
            self._cancel_job()
        else:
            response = self._responses[0]
            future = self._add_response(response.plurk_id, response.content, response.qualifier)
            future.add_done_callback(self._result)

    def _result(self, future: Future):
        result = future.result()
        if result is None:
            self._retry -= 1
            if self._retry <= 0:
                logging.error("Reach retry limit. Cancel the job.")
                self._cancel_job()
            else:
                self._job.run()
        else:
            self._responses.pop(0)
            if len(self._responses) <= 0:
                self._cancel_job()

    def _cancel_job(self):
        self._scheduler.cancel_job(self._job)


class Response:
    def __init__(self, plurk_id: int, content: str, qualifier: str):
        self.plurk_id = plurk_id  # type:int
        self.content = content  # type:str
        self.qualifier = qualifier  # type:str


def simple_response(plurk_id: int, content: List[str], qualifier: str) -> List[Response]:
    return [Response(plurk_id, text, qualifier) for text in content]


class GetResponseTask(Task):
    def __init__(self, bot: Bot, plurk_id: int, callback: Callable, period: int = 30, retry: int = 3):
        super().__init__(bot)
        self._job = self._scheduler.every(period).seconds.do(self._response)  # type:Job
        self._retry = retry  # type:int
        self._plurk_id = plurk_id  # type:int
        self._callback = callback  # type:Callable

    def _response(self):
        future = self._get_responses(self._plurk_id)
        future.add_done_callback(self._result)

    def _result(self, future: Future):
        result = future.result()
        if result is None:
            self._retry -= 1
            if self._retry <= 0:
                logging.error("Reach retry limit. Cancel the job.")
                self._cancel_job()
            else:
                self._job.run()
        else:
            self._cancel_job()
            try:
                responses = result["responses"]  # type:List[dict]
            except (TypeError, AttributeError, KeyError) as e:
                logger.error(f"error={e}, response={result}")
            else:
                if isinstance(responses, list):
                    self._callback(responses)

    def _cancel_job(self):
        self._scheduler.cancel_job(self._job)


def get_public_profiles(bot: Bot, user_ids: List[Union[str, int]]) -> List[str]:
    futures = [bot.request("/APP/Profile/getPublicProfile", {"user_id": user_id}) for user_id in user_ids]
    done, pending = wait(futures)
    results = []
    for future in done:
        result = future.result()
        try:
            name = result["user_info"]["display_name"]
        except (TypeError, KeyError) as e:
            logger.error(f"error={e}, response={result}")
        else:
            results.append(name)
    return results
