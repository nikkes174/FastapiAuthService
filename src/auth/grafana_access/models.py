from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.databse import Base
from src.user.utils import utcnow


class GrafanaAccessModel(AsyncAttrs, Base):
    __tablename__ = "grafana_access"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Пользователь, запрашивающий доступ к Grafana",
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        index=True,
        doc="pending | approved | rejected",
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=utcnow(),
        doc="Дата запроса доступа",
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="grafana_access",
        lazy="selectin",
    )
