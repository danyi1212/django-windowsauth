from functools import wraps
from logging import Logger, DEBUG
from re import finditer
from typing import Union, Callable, Optional, Tuple, Iterable, Any, Dict

from django.utils import timezone

from windows_auth import logger as default_logger


class LogExecutionTime:

    def __init__(self,
                 msg: Union[Callable, str],
                 logger: Logger = default_logger,
                 level: int = DEBUG,
                 context: Optional[Tuple[Iterable[Any], Dict[str, Any]]] = None):
        """
        Log execution time of a code block.
        msg may be a static string, or a method that receives the same arguments provided to the underlying function,
        that returns in a string (eg. log_execution_time(lambda self: f"Executing method for {self}").
        :param msg: Message to add with the execution time
        :param logger: Logger to be used
        :param level: The log level to use
        :param context: Tuple of args and kwargs to use in msg callback
        """
        self.msg = msg
        self.logger = logger
        self.level = level
        self.start_time = None
        self.context = context

    def _get_message(self) -> str:
        if not callable(self.msg):
            return f"{self.msg}: {timezone.now() - self.start_time}"
        args, kwargs = self.context or ([], {})
        return f"{self.msg(*args, **kwargs)}: {timezone.now() - self.start_time}"

    def __enter__(self):
        self.start_time = timezone.now()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.log(self.level, self._get_message())


def log_execution_time(msg: Union[Callable, str], logger: Logger = default_logger, level: int = DEBUG):
    """
    Log execution time for function.
    msg may be a static string, or a method that receives the same arguments provided to the underlying function,
    that returns in a string (eg. log_execution_time(lambda self: f"Executing method for {self}").
    :param msg: Message to add with the execution time
    :param logger: Logger to be used
    :param level: The log level to use
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with LogExecutionTime(msg, logger, level, context=(args, kwargs)):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def camel_case_split(value):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', value)
    return " ".join(m.group(0) for m in matches)
