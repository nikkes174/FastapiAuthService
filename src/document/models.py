import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.databse import Base
from src.user.utils import utcnow
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.user.models import UserModel


class DocumentModel(AsyncAttrs, Base):

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Внутренний UUID документа",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        doc="ID администратора, которому принадлежит документ",
    )

    title: Mapped[str] = mapped_column(
        String(256), nullable=False, doc="Название документа"
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=utcnow(),
        doc="Дата создания документа",
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="documents"
    )
