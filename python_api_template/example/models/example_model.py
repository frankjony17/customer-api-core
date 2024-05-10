from datetime import date

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from python_api_template.common.models.base_model import BaseOrmModel
from python_api_template.common.models.timestamp_mixin_model import TimestampMixin
from python_api_template.common.models.utils import str_255
from python_api_template.common.models.uuid_mixin_model import UuidMixin
from python_api_template.example.enums import ExampleStatusEnum


class ExampleModel(BaseOrmModel, UuidMixin, TimestampMixin):
    example_name: Mapped[str_255] = mapped_column(
        CheckConstraint(
            r"example_name ~ '^[a-zA-Z0-9\s\-_.]{1,255}$'", name="example_name_check"
        ),
        nullable=False,
    )
    example_date: Mapped[date] = mapped_column(nullable=False)
    example_number: Mapped[int] = mapped_column(
        CheckConstraint(
            "example_number >= 1 AND example_number <= 12", name="example_number_check"
        ),
        default=1,
        nullable=True,
    )
    example_status: Mapped[ExampleStatusEnum] = mapped_column(
        default=ExampleStatusEnum.A,
    )
    example_boolean: Mapped[bool] = mapped_column(default=True, nullable=False)
