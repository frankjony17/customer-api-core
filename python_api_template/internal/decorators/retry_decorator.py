import asyncio
from typing import Any, Awaitable, Callable, TypeVar
from functools import wraps

from loguru import logger
from pydantic import BaseModel

from .utils.format_func_and_args_name import format_func_and_args_name

T = TypeVar("T")


class RetryConfig(BaseModel):
    enabled: bool = True
    max_attempts: int = 3
    delay: float = 1.0
    log_retries: bool = False
    log_level: str = "DEBUG"


def retry(config: RetryConfig = RetryConfig()):
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(wrapped=func)
        async def wrapped(*args: Any, **kwargs: Any) -> T:
            logger_ = logger.opt(depth=1)
            func_name, _ = format_func_and_args_name(func, args)
            attempt = 1
            while attempt <= config.max_attempts:
                try:
                    if config.log_retries:
                        logger_.log(
                            config.log_level,
                            "[+] Executing function {}, attempt={}",
                            func_name,
                            attempt,
                        )
                    return await func(*args, **kwargs)
                except Exception as e:
                    if config.log_retries:
                        logger_.log(
                            config.log_level,
                            "[*] Execution of function {} failed on attempt {}/{}",
                            func_name,
                            attempt,
                            config.max_attempts,
                        )
                    if attempt < config.max_attempts:
                        if config.log_retries:
                            logger_.log(
                                config.log_level,
                                "[*] Retrying function {} after {}s",
                                func_name,
                                config.delay,
                            )
                        await asyncio.sleep(config.delay)
                        attempt += 1
                    else:
                        if config.log_retries:
                            logger_.log(
                                config.log_level,
                                "[x] All retries of function {} failed.",
                                func_name,
                            )
                        raise e

            # Adding an explicit raise here to clarify that the function should
            # never reach this point, just to satisfy the type-checker
            raise RuntimeError(
                f"All retries failed for {func_name}; last exception handled"
            )

        return wrapped

    return decorator
