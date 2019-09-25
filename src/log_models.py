import os
import pathlib
import logging
from logging.handlers import RotatingFileHandler

# make directory path and parent folders if not exists
def mkdir_p(path):
    try:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    except FileExistsError as exc:
        pass

class MyLoggerFactory:
    @staticmethod
    def getLogger(name):

        LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
        LOG_NAME = name
        LOG_FILE_ERROR = 'log/server.log'

        logger = logging.getLogger(LOG_NAME)

        log_formatter = logging.Formatter(LOG_FORMAT)

        file_handler_error = MyRotatingFileHandler(filename=LOG_FILE_ERROR, maxBytes=10*1024*1024, backupCount=5)
        file_handler_error.setFormatter(log_formatter)
        file_handler_error.setLevel(logging.DEBUG)

        logger.addHandler(file_handler_error)

        logger.setLevel(logging.DEBUG)

        return logger

class MyRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        mkdir_p(os.path.dirname(filename))
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)
