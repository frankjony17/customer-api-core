from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from python_api_template.common.base_service import BaseService

from ..common.enums import SortOrder
from .enums import ExampleSortKey, ExampleStatusEnum
from .models import ExampleModel
from .repository import ExampleRepository
from .schemas import CreateExampleSchema, GetExampleSchema


class ExampleService(BaseService):
    def __init__(self, async_session: AsyncSession):
        self.repository = ExampleRepository(async_session)

    async def get_example(
        self,
        example_date: date,
        example_status: ExampleStatusEnum,
        sort_order: SortOrder = SortOrder.ASC,
        sort_key: ExampleSortKey = ExampleSortKey.STATUS,
        skip: int = 0,
        limit: int = 100,
    ) -> list[GetExampleSchema]:
        _example_date = datetime.combine(example_date, time()) if example_date else None

        examples = await self.repository.find_example(
            example_date=_example_date,
            example_status=example_status,
            sort_order=sort_order,
            sort_key=sort_key,
            skip=skip,
            limit=limit,
        )
        return list(map(GetExampleSchema.model_validate, examples))

    async def get_example_by_id(self, example_id: UUID) -> GetExampleSchema:
        payment_calendar = await self.repository.find_one(ExampleModel, example_id)
        return GetExampleSchema.model_validate(payment_calendar)

    async def create(self, example_schema: CreateExampleSchema):
        example_model = ExampleModel(
            example_name=example_schema.example_name,
            example_date=example_schema.example_date,
            example_number=example_schema.example_number,
            example_status=example_schema.example_status,
            example_boolean=example_schema.example_boolean,
        )
        example = await self.repository.save(example_model)

        return GetExampleSchema.model_validate(example)

    async def delete(self, example_id: UUID):
        await self.repository.delete(ExampleModel, example_id)
