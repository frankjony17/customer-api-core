from typing import Any
from urllib.parse import urljoin

from httpx import AsyncClient, HTTPStatusError, Response
from httpx._types import RequestFiles
from loguru import logger
from starlette import status

from python_api_template.common.exceptions.enums import RequestMethod
from python_api_template.common.exceptions.exceptions import (
    BadRequestError,
    ForbiddenError,
    MethodNotAllowedError,
    NotFoundError,
    ServiceUnavailableError,
    UnauthorizedError,
    UnprocessableEntityError,
)

from ..config.settings import global_settings
from .decorators import http_retry


class HttpClient:
    def __init__(self, host: str):
        self.host = host
        self.headers = global_settings.http.basic_headers
        self.timeout = global_settings.http.timeout
        self.max_attempts = global_settings.http.max_attempts
        self.time_sleep = global_settings.http.time_sleep

    async def _get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Response:
        if headers:
            self.headers.update(headers)
        async with AsyncClient() as client:
            return await client.get(
                url, headers=self.headers, params=params, timeout=self.timeout
            )

    async def _post(
        self,
        url: str,
        auth: tuple[str, str] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        files: RequestFiles | None = None,
    ) -> Response:
        if headers:
            headers.update(self.headers)
        async with AsyncClient() as client:
            if auth:
                return await client.post(
                    url,
                    headers=headers,
                    auth=auth,
                    data=data,
                    files=files,
                    timeout=self.timeout,
                )
            return await client.post(
                url,
                headers=headers,
                data=data,
                files=files,
                timeout=self.timeout,
            )

    async def _put(
        self,
        url: str,
        auth: tuple[str, str] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        files: RequestFiles | None = None,
    ) -> Response:
        if headers:
            headers.update(self.headers)
        async with AsyncClient() as client:
            if auth:
                return await client.put(
                    url,
                    headers=headers,
                    auth=auth,
                    data=data,
                    files=files,
                    timeout=self.timeout,
                )
            return await client.put(
                url,
                headers=headers,
                data=data,
                files=files,
                timeout=self.timeout,
            )

    @http_retry
    async def request(
        self,
        path: str,
        method: RequestMethod,
        data: dict[str, Any] | None = None,
        auth: tuple[str, str] | None = None,
        files: RequestFiles | None = None,
    ) -> Any:
        url = urljoin(self.host, path)

        try:
            if files and method == RequestMethod.GET:
                raise MethodNotAllowedError(
                    detail=f"Method {method} not allowed",
                    url=url,
                )
            if method == RequestMethod.GET:
                response = await self._get(url, params=data)
            elif method == RequestMethod.POST:
                response = await self._post(url, auth=auth, data=data, files=files)
            elif method == RequestMethod.PUT:
                response = await self._put(url, auth=auth, data=data, files=files)
            else:
                raise MethodNotAllowedError(
                    detail=f"Method {method} not allowed",
                    url=url,
                )

            logger.info(
                f"[+] request made. [url={url}] - "
                f"[status_code={response.status_code}]"
            )

            response.raise_for_status()
            return response.json()

        except HTTPStatusError as e:
            match e.response.status_code:
                case status.HTTP_400_BAD_REQUEST:
                    raise BadRequestError(e.response.text, url=url) from e
                case status.HTTP_401_UNAUTHORIZED:
                    raise UnauthorizedError(e.response.text, url=url) from e
                case status.HTTP_404_NOT_FOUND:
                    raise NotFoundError(e.response.text, url=url) from e
                case status.HTTP_403_FORBIDDEN:
                    raise ForbiddenError(e.response.text, url=url) from e
                case status.HTTP_422_UNPROCESSABLE_ENTITY:
                    raise UnprocessableEntityError(e.response.text, url=url) from e
                case _:
                    raise ServiceUnavailableError(
                        detail=e.response.text, url=url
                    ) from e
