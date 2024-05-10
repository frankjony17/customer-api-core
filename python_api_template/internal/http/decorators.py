from __future__ import annotations

import asyncio
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable

import httpx
from loguru import logger

from python_api_template.common.exceptions.exceptions import TooManyRequestsError

if TYPE_CHECKING:
    from .client import HttpClient


def http_retry(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapped_func(self: HttpClient, *args: Any, **kwargs: Any) -> Any:
        max_attempts: int = getattr(self, "max_attempts")
        time_sleep: float = getattr(self, "time_sleep")

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"[+] Sending request - [attempt={attempt}]")
                response: Any = await func(self, *args, **kwargs)
                return response
            except httpx.RequestError as error:
                logger.warning(
                    f"[*] Request failed on attempt {attempt}/{max_attempts}. Error: {error}"
                )

                if attempt < max_attempts:
                    logger.info(f"[*] Retrying after {time_sleep}s.")
                    await asyncio.sleep(time_sleep)
                else:
                    logger.error("[X] All retry attempts failed.")
                    raise TooManyRequestsError("") from error

    return wrapped_func
