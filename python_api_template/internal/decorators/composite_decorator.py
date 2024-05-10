from .exception_decorator import exceptions_wrapper, ExceptionsWrapperConfig
from .logger_decorator import log_wrapper, LogWrapperConfig
from .retry_decorator import retry, RetryConfig
from .timeit_decorator import timeit, TimeItConfig


from typing import Callable, Awaitable, TypeVar

T = TypeVar("T")


def composite_decorator(
    retry_config: RetryConfig,
    time_it_config: TimeItConfig,
    log_wrapper_config: LogWrapperConfig,
    exceptions_wrapper_config: ExceptionsWrapperConfig,
):
    def apply_decorators(
        func: Callable[..., Awaitable[T]],
    ) -> Callable[..., Awaitable[T]]:
        if exceptions_wrapper_config.enabled:
            func = exceptions_wrapper(exceptions_wrapper_config)(func)
        if log_wrapper_config.enabled:
            func = log_wrapper(log_wrapper_config)(func)
        if time_it_config.enabled:
            func = timeit(time_it_config)(func)
        if retry_config.enabled:
            func = retry(retry_config)(func)
        return func

    return apply_decorators


if __name__ == "__main__":
    import asyncio
    from sqlalchemy.exc import NoResultFound
    import random
    from loguru import logger
    from python_api_template.internal.decorators.decorator_metaclass import (
        DecoratorMetaclass,
    )

    class MyClass(metaclass=DecoratorMetaclass):
        retry_config = RetryConfig(
            enabled=True, max_attempts=3, delay=1, log_retries=True
        )
        time_it_config = TimeItConfig(enabled=True, log_exec_time=True)
        log_wrapper_config = LogWrapperConfig(
            enabled=True,
            log_entry=True,
            log_exit=True,
            log_error=True,
            log_level="DEBUG",
        )
        exceptions_wrapper_config = ExceptionsWrapperConfig(
            enabled=True, log_exceptions=True
        )

        async def sample_function(self, p=0.5, a=1, b=2):
            logger.debug("Function execution")
            await asyncio.sleep(1)
            if random.random() < p:
                raise NoResultFound
            return "Success"

    my_class = MyClass()

    asyncio.run(my_class.sample_function(p=0.1))

    # @composite_decorator(
    #     retry_config=RetryConfig(enabled=False, max_attempts=3, delay=1, log_retries=True),
    #     time_it_config=TimeItConfig(enabled=True, log_exec_time=True),
    #     log_wrapper_config=LogWrapperConfig(
    #         enabled=False, log_entry=True, log_exit=True, log_error=True, log_level="DEBUG"
    #     ),
    #     exceptions_wrapper_config=ExceptionsWrapperConfig(enabled=False, log_exceptions=True),
    # )
    # async def sample_function(p=0.5):
    #     logger.debug("Function execution")
    #     await asyncio.sleep(1)
    #     if random.random() < p:
    #         raise NoResultFound
    #     return "Success"
    # asyncio.run(sample_function(0.1))
