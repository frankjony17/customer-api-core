import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from python_api_template.internal.db import ExampleModel
from python_api_template.example.enums.example_status import ExampleStatusEnum
from python_api_template.example.schemas.create_example import CreateExampleSchema
from python_api_template.example.service import ExampleService


async def test_orm(session: AsyncSession):
    example_in = CreateExampleSchema(
        example_name="Michael",
        example_date="2021-01-01",
        example_number=1,
        example_status=ExampleStatusEnum.A,
        example_boolean=True,
    )
    service = ExampleService(session)
    example_in_db = await service.create(example_in)

    example_list = await service.get_example(
        example_date=date(2021, 1, 1),
        example_status=ExampleStatusEnum.A,
        limit=1,
    )
    example_out = example_list[0]

    assert example_in_db == example_out


async def test_session(session: AsyncSession):
    example_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    example_obj = ExampleModel(
        id=example_id,
        example_name="example_name",
        example_date=date(2022, 1, 1),
        example_status=ExampleStatusEnum.A,
        created_at=created_at,
        updated_at=updated_at,
    )

    # Add `Example` object to the session
    async with session.begin():
        session.add(example_obj)

    # query for ``Example`` objects
    statement = select(ExampleModel)

    # Get the `Example` object from the session
    example_obj_in_db = (await session.scalars(statement)).first()

    assert example_obj_in_db == example_obj
