from project import ProjectBuilder
from task import FriendTask, PlurkTask
import logging
import sys

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s [%(levelname)s] <%(thread)d> %(filename)s(%(lineno)d): %(message)s",
                        level=logging.NOTSET)
    if len(sys.argv) != 5:
        logging.error(f"Invalid Parameters: {sys.argv}")
    else:
        p = ProjectBuilder(*sys.argv[1:])
        p.worker(3).task(PlurkTask(), FriendTask()).build().start()
