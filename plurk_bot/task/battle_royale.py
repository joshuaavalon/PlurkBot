import logging

from plurk_bot.bot import Bot
from plurk_bot.task.event import NewPlurkEvent
from plurk_bot.task.task import ResponseTask, simple_response, GetResponseTask, get_public_profiles

__all__ = ["BattleRoyaleListener"]
logger = logging.getLogger(__name__)


class BattleRoyaleListener:
    def __init__(self, bot: Bot, auto_start=True):
        self._bot = bot  # type:Bot
        if auto_start:
            self.start()

    def _receive(self, event):
        for plurk in event.plurks:
            try:
                if "qualifier" in plurk and plurk["qualifier"] == "needs" and "content" in plurk and \
                        plurk["content_raw"].startswith("Test"):
                    #ResponseTask(self._bot, simple_response(plurk["plurk_id"], ["1"], ":"))
                    GetResponseTask(self._bot, plurk["plurk_id"], self._join)
            except (TypeError, KeyError) as e:
                logger.error(f"plurk={plurk}, error={e}")

    def _join(self, responses):

        players = set([response["user_id"] for response in responses if response is not None and "user_id" in response
                       and "content_raw" in response and response["content_raw"].startswith("報名") and
                       "qualifier" in response and response["qualifier"] == "wants"])
        print(players)
        print(get_public_profiles(self._bot, players))

    def stop(self):
        self._bot.unsubscribe(NewPlurkEvent, self._receive)

    def start(self):
        self._bot.subscribe(NewPlurkEvent, self._receive)
