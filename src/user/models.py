import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.databse import Base
from src.document.models import DocumentModel
from src.user.utils import utcnow

if TYPE_CHECKING:
    from src.role.models import RoleModel


class UserModel(AsyncAttrs, Base):

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Внутренний UUID пользователя",
    )

    user_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True,
        doc='Уникальный никнейм пользователя',
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="Уникальный email пользователя",
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="Хэш пароля пользователя"
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=utcnow(), doc="Дата создания пользователя"
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=utcnow(),
        server_onupdate=utcnow(),
        onupdate=utcnow(),
        doc="Дата обновления пользователя",
    )

    documents: Mapped[list["DocumentModel"]] = relationship(
        "DocumentModel", back_populates="user", passive_deletes=True
    )

    roles: Mapped[list["RoleModel"]] = relationship(
        secondary="user_roles", back_populates="users", lazy="selectin"
    )

    grafana_access: Mapped["GrafanaAccessModel | None"] = relationship(
        "GrafanaAccessModel",
        back_populates="user",
        uselist=False,
        passive_deletes=True,
    )
