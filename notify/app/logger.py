import logging
import os
import sys
from enum import Enum

import notify.logs


class LoggerType(Enum):
    USER = 'user'
    EVENT = 'event'
    EXCEPTION = 'exception'
    WEATHER = 'weather'
    MAIL = 'mail'
    CELERY = 'celery'


def get_path(filename: str) -> str:
    path = os.path.dirname(notify.logs.__file__)
    return os.path.join(path, f'{filename}.log')


def create_logger(filename_type: LoggerType, name: str) -> logging.Logger:
    """Create a logger with the specified name and filename. Logger handlers are set to write to a file and stdout."""
    filename = filename_type.value
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    file_path = get_path(filename)
    handler = logging.FileHandler(file_path, mode='a', encoding='utf-8')
    formatter = logging.Formatter(datefmt='%Y-%m-%d %H:%M:%S',
                                  fmt='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

    handler.setFormatter(formatter)
    output_handler = logging.StreamHandler(sys.stdout)
    output_handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(output_handler)

    return logger

"""Logger for uncaught exceptions."""
e_logger = create_logger(LoggerType.EXCEPTION, 'LOG')


def my_handler(type, value, tb):
    e_logger.exception(f"Uncaught exception: {value}")


sys.excepthook = my_handler
