from functools import wraps
from typing import Union, Callable

from django.utils import timezone

from windows_auth import logger


def debug_exec_time(msg: Union[Callable, str]):
    """
    Log execution time for function.
    msg may be a static string, or a method that receives the same arguments provided to the underlying function,
    that returns in a string (eg. debug_exec_time(lambda self: f"Executing method for {self}").
    :param msg: Message to add with the execution time
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = timezone.now()
            # execute original function
            results = func(*args, **kwargs)
            if callable(msg):
                logger.debug(f"{msg(*args, **kwargs)}: {timezone.now() - start_time}")
            else:
                logger.debug(f"{msg}: {timezone.now() - start_time}")
            return results
        return wrapper
    return decorator