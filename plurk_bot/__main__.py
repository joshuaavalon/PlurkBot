import logging
from argparse import ArgumentParser, RawTextHelpFormatter
from logging.handlers import RotatingFileHandler
from os import makedirs
from os.path import join, dirname

from plurk_api import PlurkApi

from plurk_bot.bot import Bot
from plurk_bot.task import *

logo = """\
__________.__                __     __________        __   
\______   |  |  __ _________|  | __ \______   \ _____/  |_ 
 |     ___|  | |  |  \_  __ |  |/ /  |    |  _//  _ \   __\ 
 |    |   |  |_|  |  /|  | \|    <   |    |   (  <_> |  |  
 |____|   |____|____/ |__|  |__|_ \  |______  /\____/|__|  
                                 \/         \/             
"""


def main():
    log_folder = join(dirname(__file__), "..", "log")
    log_file = join(log_folder, "app.log")
    makedirs(log_folder, exist_ok=True)
    logging.basicConfig(format="%(asctime)s [%(levelname)s] <%(thread)d> %(filename)s(%(lineno)d): %(message)s",
                        level=logging.INFO)#,
                       #handlers=[
                        #    RotatingFileHandler(log_file, maxBytes=1048576, backupCount=3, encoding="utf-8")])
    parser = ArgumentParser(description=logo, formatter_class=RawTextHelpFormatter)
    parser.add_argument("app_key", type=str, help="App key")
    parser.add_argument("app_secret", type=str, help="App secret")
    parser.add_argument("token_key", type=str, help="Access token key")
    parser.add_argument("token_secret", type=str, help="Access token secret")
    args = parser.parse_args()
    logging.info("\n" + logo)
    api = PlurkApi(args.app_key, args.app_secret, args.token_key, args.token_secret, timeout=30,
                   disable_ssl_certificate_validation=True)
    bot = Bot(api, 4)
    FriendTask(bot)
    TimeLineListenerTask(bot)
    BattleRoyaleListener(bot)
    bot.start()


if __name__ == "__main__":
    main()
