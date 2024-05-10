from datetime import date
from typing import Any

from sqlalchemy import Select, asc, desc, select

from python_api_template.common.enums.base_enum import BaseEnum
from python_api_template.common.enums.sort import SortOrder
from python_api_template.example.enums.example_sort_key import ExampleSortKey

from ..common.base_repository import BaseRepository
from .enums import ExampleStatusEnum
from .models.example_model import ExampleModel


class ExampleRepository(BaseRepository[ExampleModel]):
    async def find_example(
        self,
        example_date: date | None,
        example_status: ExampleStatusEnum,
        sort_order: SortOrder,
        sort_key: ExampleSortKey,
        skip: int,
        limit: int,
    ):
        stmt = select(ExampleModel)

        if example_date:
            stmt = stmt.where(ExampleModel.example_date >= example_date)
        if example_status:
            stmt = stmt.where(ExampleModel.example_status == example_status)
        if sort_order:
            stmt = self._order_by(stmt, sort_order, sort_key)

        stmt = stmt.offset(skip).limit(limit)

        return (await self.async_session.execute(stmt)).scalars().all()

    @classmethod
    def _order_by(
        cls,
        stmt: Select[Any],
        sort_order: SortOrder,
        sort_key: BaseEnum,
    ) -> Select[Any]:
        sort_func = asc if sort_order == SortOrder.ASC else desc
        return stmt.order_by(sort_func(getattr(ExampleModel, sort_key.value)))
