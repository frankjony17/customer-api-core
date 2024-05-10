from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel
from starlette import status

from python_api_template.common.enums.sort import SortOrder
from python_api_template.common.schemas.problem_details_v1 import ProblemDetailsV1
from python_api_template.example.enums.example_sort_key import ExampleSortKey
from python_api_template.example.enums.example_status import ExampleStatusEnum
from python_api_template.example.schemas import CreateExampleSchema, GetExampleSchema

from ..dependencies import ExampleServiceDependency

router = APIRouter()


@router.get(
    "/",
    responses={
        status.HTTP_200_OK: {
            "model": list[GetExampleSchema],
            "description": "List of all examples",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ProblemDetailsV1,
            "description": "Bad Request",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ProblemDetailsV1,
            "description": "Unauthorized",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ProblemDetailsV1,
            "description": "Forbidden",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ProblemDetailsV1,
            "description": "Not found",
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "model": ProblemDetailsV1,
            "description": "Not acceptable",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ProblemDetailsV1,
            "description": "Validation Error",
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "model": ProblemDetailsV1,
            "description": "Too many requests",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ProblemDetailsV1,
            "description": "Internal error",
        },
    },
    summary="Returns a list of all examples",
    response_model_by_alias=True,
)
async def get_examples(
    example_service: ExampleServiceDependency,
    example_date: Optional[date] = Query(
        None, description="Start of next_payment_date"
    ),
    example_status: ExampleStatusEnum = Query(
        ExampleStatusEnum.A, description="Status of example"
    ),
    sort_order: SortOrder = Query(
        SortOrder.ASC, description="Order of the items listed"
    ),
    sort_key: ExampleSortKey = Query(
        ExampleSortKey.STATUS, description="Field used for sorting"
    ),
    skip: int = Query(
        0,
        description="Number of items to skip at the beginning of the list",
        ge=0,
        le=1000000,
    ),
    limit: int = Query(
        20,
        description="Maximum number of items to be returned at the same time",
        ge=0,
        le=100,
    ),
):
    return await example_service.get_example(
        example_date,
        example_status,
        sort_order,
        sort_key,
        skip,
        limit,
    )


@router.get(
    "/{example_id}",
    responses={
        status.HTTP_200_OK: {
            "model": GetExampleSchema,
            "description": "Example by Id",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ProblemDetailsV1,
            "description": "Bad Request",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ProblemDetailsV1,
            "description": "Unauthorized",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ProblemDetailsV1,
            "description": "Forbidden",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ProblemDetailsV1,
            "description": "Not found",
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "model": ProblemDetailsV1,
            "description": "Not acceptable",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ProblemDetailsV1,
            "description": "Validation Error",
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "model": ProblemDetailsV1,
            "description": "Too many requests",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ProblemDetailsV1,
            "description": "Internal error",
        },
    },
    response_model=GetExampleSchema,
    summary="Returns a example by its identification",
)
async def get_example(
    example_id: UUID,
    example_service: ExampleServiceDependency,
):
    return await example_service.get_example_by_id(example_id)


@router.post(
    "/",
    responses={
        status.HTTP_200_OK: {
            "model": CreateExampleSchema,
            "description": "Create Example schema",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ProblemDetailsV1,
            "description": "Bad Request",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ProblemDetailsV1,
            "description": "Unauthorized",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ProblemDetailsV1,
            "description": "Forbidden",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ProblemDetailsV1,
            "description": "Not found",
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "model": ProblemDetailsV1,
            "description": "Not acceptable",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ProblemDetailsV1,
            "description": "Validation Error",
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "model": ProblemDetailsV1,
            "description": "Too many requests",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ProblemDetailsV1,
            "description": "Internal error",
        },
    },
    response_model=GetExampleSchema,
    description="Creates a example with the given data",
)
async def create_example(
    example_service: ExampleServiceDependency,
    example_schema: CreateExampleSchema,
):
    return await example_service.create(example_schema)


@router.delete("/{example_id}")
async def delete_example(
    example_id: UUID,
    example_service: ExampleServiceDependency,
):
    await example_service.delete(example_id)
    return {"message": "Example deleted successfully"}
