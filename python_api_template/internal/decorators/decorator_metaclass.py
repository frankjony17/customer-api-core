from .exception_decorator import ExceptionsWrapperConfig
from .logger_decorator import LogWrapperConfig
from .retry_decorator import RetryConfig
from .timeit_decorator import TimeItConfig
from .composite_decorator import composite_decorator


class DecoratorMetaclass(type):
    def __new__(cls, name, bases, local):
        retry_config = local.get(
            "retry_config",
            RetryConfig(enabled=False, max_attempts=1, delay=0, log_retries=False),
        )
        time_it_config = local.get(
            "time_it_config", TimeItConfig(enabled=False, log_exec_time=False)
        )
        log_wrapper_config = local.get(
            "log_wrapper_config",
            LogWrapperConfig(
                enabled=False,
                log_entry=False,
                log_exit=False,
                log_error=False,
                log_level="INFO",
            ),
        )
        exceptions_wrapper_config = local.get(
            "exceptions_wrapper_config",
            ExceptionsWrapperConfig(enabled=False, log_exceptions=False),
        )

        decorator = composite_decorator(
            retry_config, time_it_config, log_wrapper_config, exceptions_wrapper_config
        )

        for key, value in list(local.items()):
            if callable(value) and not key.startswith("__"):
                local[key] = decorator(value)
        return type.__new__(cls, name, bases, local)
