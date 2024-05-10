import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import TIMESTAMP
from sqlalchemy import Enum as SaEnum
from sqlalchemy import MetaData, String, event
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, declared_attr, registry

from python_api_template.internal.config.settings import global_settings

from ..enums.base_enum import BaseEnum
from .utils import CONVENTION, camel_to_snake, str_3, str_36, str_255


# Rename enum types in database
# Not super cleanly, using schema events, since the name here is part of Enum's
# participation in schema DDL
@event.listens_for(SaEnum, "before_parent_attach")
def receive_before_parent_attach(target, parent):
    if target.name == "ASSIGN":
        target.name = camel_to_snake(target.enum_class.__name__)


@dataclass
class BaseOrmModel(AsyncAttrs, DeclarativeBase, MappedAsDataclass, kw_only=True):
    """
    BaseModel is a base class for ORM entities.
    It extends SQLAlchemy's declarative base class, and sets some default table arguments.

    It has the following attributes:

    - `__abstract__`: A class attribute that suggests this class should not be instantiated
                      directly. In SQLAlchemy, this is often used for mixin or base classes.

    Attributes:
        __abstract__ (bool): A flag to indicate that this class is abstract and should not b
                             e instantiated.
    """

    @declared_attr.directive
    def __tablename__(cls):
        return camel_to_snake(cls.__name__).replace("_model", "")

    __abstract__ = True
    __mapper_args__ = {"eager_defaults": True}

    registry = registry(
        type_annotation_map={
            datetime: TIMESTAMP(
                timezone=True
            ),  # TIMESTAMP datatype with timezone=True for datetime.datetime,
            # https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#altering-the-configuration-of-the-default-enum
            BaseEnum: SaEnum(BaseEnum, inherit_schema=True, name="ASSIGN"),
            str_255: String(255),
            str_36: String(36),
            str_3: String(3),
            uuid.UUID: PG_UUID(as_uuid=True),
        }
    )

    metadata = MetaData(
        naming_convention=CONVENTION, schema=global_settings.postgres.db_schema
    )

    def __str__(self):
        output = ""
        for c in self.__table__.columns:
            output += f"{c.name}: {getattr(self, c.name)}"
        return output

    def __repr__(self) -> str:
        columns = ", ".join(
            [
                f"{k}={repr(v)}"
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            ]
        )
        return f"<{self.__class__.__name__}({columns})>"
