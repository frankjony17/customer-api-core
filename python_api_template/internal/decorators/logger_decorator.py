from typing import Any, Callable, TypeVar, Awaitable
from functools import wraps

from loguru import logger
from pydantic import BaseModel

from .utils.format_func_and_args_name import format_func_and_args_name

T = TypeVar("T")


class LogWrapperConfig(BaseModel):
    enabled: bool = True
    log_entry: bool = True
    log_exit: bool = True
    log_error: bool = True
    log_level: str = "DEBUG"


def log_wrapper(config: LogWrapperConfig = LogWrapperConfig()):
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapped(*args: Any, **kwargs: Any) -> T:
            logger_ = logger.opt(depth=1)
            func_name, args_repr = format_func_and_args_name(func, args)
            if config.log_entry:
                logger_.log(
                    config.log_level,
                    "[+] Entering '{}' (args={}, kwargs={})",
                    func_name,
                    args_repr,
                    kwargs,
                )
            try:
                result = await func(*args, **kwargs)
                if config.log_exit:
                    logger_.log(
                        config.log_level,
                        "[+] Exiting '{}' (result={})",
                        func_name,
                        result,
                    )
                return result
            except Exception as e:
                if config.log_error:
                    logger_.log(
                        config.log_level, "[x] Exception in '{}': {}", func_name, e
                    )
                raise Exception from e

        return wrapped

    return decorator
