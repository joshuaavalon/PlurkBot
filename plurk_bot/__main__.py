import logging
from argparse import ArgumentParser, RawTextHelpFormatter
from logging.handlers import RotatingFileHandler
import os

logo = """\
__________.__                __     __________        __   
\______   |  |  __ _________|  | __ \______   \ _____/  |_ 
 |     ___|  | |  |  \_  __ |  |/ /  |    |  _//  _ \   __\ 
 |    |   |  |_|  |  /|  | \|    <   |    |   (  <_> |  |  
 |____|   |____|____/ |__|  |__|_ \  |______  /\____/|__|  
                                 \/         \/             
"""


def main():
    os.makedirs("log", exist_ok=True)
    logging.basicConfig(format="%(asctime)s [%(levelname)s] <%(thread)d> %(filename)s(%(lineno)d): %(message)s",
                        level=logging.INFO,
                        handlers=[RotatingFileHandler("log/app.log", maxBytes=1048576, backupCount=3, encoding="utf-8")])
    parser = ArgumentParser(description=logo, formatter_class=RawTextHelpFormatter)
    parser.add_argument("app_key", type=str, help="App key")
    parser.add_argument("app_secret", type=str, help="App secret")
    parser.add_argument("token_key", type=str, help="Access token key")
    parser.add_argument("token_secret", type=str, help="Access token secret")
    args = parser.parse_args()


"""
    if len(sys.argv) != 5:
        logging.error(f"Invalid Parameters: {sys.argv}")
    else:
        builder = ProjectBuilder(*sys.argv[1:])
        builder.worker(4).task(*create_tasks()).build().start()
"""

if __name__ == "__main__":
    main()
