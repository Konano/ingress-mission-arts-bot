import logging
import sys
from logging import Filter, StreamHandler
from logging.handlers import TimedRotatingFileHandler
from typing import Any

import colorlog

from base.sentry import sentry_init

sentry_init()


BASIC_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(lineno)d - %(funcName)s - %(message)s'
COLOR_FORMAT = '%(log_color)s%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
DATE_FORMAT = None
basic_formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
color_formatter = colorlog.ColoredFormatter(COLOR_FORMAT, DATE_FORMAT)


class MaxFilter(Filter):
    def __init__(self, max_level):
        self.max_level = max_level

    def filter(self, record): # type: ignore
        if record.levelno <= self.max_level:
            return True


class EnhancedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc)

    def computeRollover(self, currentTime: int):
        """
        Work out the rollover time based on the specified time.
        """
        if self.when == 'MIDNIGHT' or self.when.startswith('W'):
            return super().computeRollover(currentTime)
        if self.when == 'D':
            # 8 hours ahead of UTC
            return currentTime - (currentTime + 8 * 3600) % self.interval + self.interval
        return currentTime - currentTime % self.interval + self.interval


chlr = StreamHandler(stream=sys.stdout)
chlr.setFormatter(color_formatter)
chlr.setLevel('INFO')
chlr.addFilter(MaxFilter(logging.INFO))

ehlr = StreamHandler(stream=sys.stderr)
ehlr.setFormatter(color_formatter)
ehlr.setLevel('WARNING')

fhlr = EnhancedRotatingFileHandler('log/server.log', when='H', interval=1, backupCount=24*7)
fhlr.setFormatter(basic_formatter)
fhlr.setLevel('DEBUG')

# 日志默认设置
logger = logging.getLogger()
logger.setLevel('INFO')
logger.addHandler(fhlr)

# 模组调用: telegram
logging.getLogger('telegram').setLevel('DEBUG')

# # 模组调用: apscheduler
# logging.getLogger('apscheduler').setLevel('DEBUG')

# 自行调用
logger = logging.getLogger('main')
logger.setLevel('DEBUG')
logger.addHandler(chlr)
logger.addHandler(ehlr)

UNICORN_LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": True,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
            "use_colors": True,
        },
        "access_file": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
            "use_colors": False,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            # "stream": "ext://sys.stderr",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access_file": {
            "formatter": "access_file",
            # "class": "logging.handlers.TimedRotatingFileHandler",
            "class": "base.log.EnhancedRotatingFileHandler",
            "filename": "log/unicorn.log",
            "when": "D",
            "interval": 1,
            "backupCount": 14,
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access_file"], "level": "DEBUG", "propagate": False},
    },
}
