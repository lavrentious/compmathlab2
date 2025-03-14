from enum import Enum
from io import TextIOWrapper
from typing import Any


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    file: None | TextIOWrapper | Any
    min_level = LogLevel.INFO

    def __init__(self, file=None, min_level=LogLevel.INFO):
        self.file = file
        self.min_level = min_level

    def set_min_level(self, min_level: LogLevel):
        self.min_level = min_level

    def log(
        self,
        *args: Any,
        level: LogLevel = LogLevel.INFO,
        sep: str = " ",
        end: str = "\n",
    ) -> None:
        if level._sort_order_ < self.min_level._sort_order_:
            return
        print(f"[{level.value}]", *args, sep=sep, end=end, file=self.file)

    def debug(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        self.log(*args, level=LogLevel.DEBUG, sep=sep, end=end)

    def info(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        self.log(*args, level=LogLevel.INFO, sep=sep, end=end)

    def warning(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        self.log(*args, level=LogLevel.WARNING, sep=sep, end=end)

    def error(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        self.log(*args, level=LogLevel.ERROR, sep=sep, end=end)

    def critical(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        self.log(*args, level=LogLevel.CRITICAL, sep=sep, end=end)


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class GlobalLogger(Logger):
    pass
