import time
from typing import Any, Callable, Awaitable, TypeVar
from functools import wraps

from loguru import logger
from pydantic import BaseModel

from .utils.format_func_and_args_name import format_func_and_args_name

T = TypeVar("T")


class TimeItConfig(BaseModel):
    enabled: bool = True
    max_attempts: int = 3
    delay: float = 1.0
    log_exec_time: bool = False
    log_level: str = "DEBUG"


def timeit(config: TimeItConfig = TimeItConfig()):
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapped(*args: Any, **kwargs: Any) -> T:
            func_name, _ = format_func_and_args_name(func, args)
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            end = time.perf_counter()
            if config.log_exec_time:
                logger_ = logger.opt(depth=1)
                logger_.log(
                    config.log_level,
                    "[+] Function '{}' executed in {:f} s",
                    func_name,
                    end - start,
                )
            return result

        return wrapped

    return decorator
