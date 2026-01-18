from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from src.user.schemas import UserRead


class DocumentBase(BaseModel):
    title: str


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    id: UUID
    user_id: UUID | None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentWithUser(DocumentRead):
    user: "UserRead | None"


class DocumentUpdate(BaseModel):
    title: str


class DocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str

    model_config = ConfigDict(from_attributes=True)
