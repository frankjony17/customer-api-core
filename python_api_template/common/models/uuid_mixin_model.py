import uuid

from sqlalchemy import func
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

from .utils import generate_uuid


class UuidMixin(MappedAsDataclass):
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default_factory=generate_uuid,
        index=True,
        nullable=False,
        unique=True,
        server_default=func.gen_random_uuid(),
    )
