from typing import Annotated

from fastapi import Depends

from python_api_template.dependencies import AsyncSessionDependency
from python_api_template.example.service import ExampleService


def get_example_service(
    async_session: AsyncSessionDependency,
) -> ExampleService:
    return ExampleService(async_session)


ExampleServiceDependency = Annotated[ExampleService, Depends(get_example_service)]
