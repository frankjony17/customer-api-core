from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class TimestampMixin(MappedAsDataclass):
    created_at: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        server_default=func.CURRENT_TIMESTAMP(0),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        server_default=func.CURRENT_TIMESTAMP(0),
        onupdate=func.CURRENT_TIMESTAMP(0),
    )
