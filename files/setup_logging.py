# This file exists to setup Gary's logging structure.
# It's split off to make code structure easier to undersatnd.

import logging
from logging.handlers import RotatingFileHandler

class GaryLogging:

    def __init__(self):
        log_formatter = logging.Formatter("%(asctime)s %(levelname)s: [%(filename)s] [%(funcName)s](%(lineno)d) %(message)s")

        log_file = "files//logs//gary.log"

        my_handler = RotatingFileHandler(log_file, mode="a", maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=False)

        my_handler.setFormatter(log_formatter)
        my_handler.setLevel(logging.INFO)

        self.log = logging.getLogger("root")
        self.log.setLevel(logging.INFO)

        self.log.addHandler(my_handler)