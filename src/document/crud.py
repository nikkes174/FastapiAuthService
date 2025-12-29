from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.document.models import DocumentModel
from src.document.schemas import DocumentUpdate


class DocumentCrud:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, title: str, user_id: UUID):
        document = DocumentModel(
            title=title,
            user_id=user_id,
        )
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_by_id(
        self,
        document_id: UUID,
    ) -> DocumentModel | None:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        return result.scalar_one_or_none()

    async def search_by_title(
        self,
        title: str,
    ) -> list[DocumentModel]:
        result = await self.session.execute(
            select(DocumentModel)
            .where(DocumentModel.title.ilike(f"%{title}%"))
            .order_by(DocumentModel.created_at.desc())
        )
        return result.scalars().all()

    async def update(
        self,
        document: DocumentModel,
        data: DocumentUpdate,
    ) -> DocumentModel:
        document.title = data.title

        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def delete(
        self,
        document: DocumentModel,
    ) -> None:
        await self.session.delete(document)
        await self.session.commit()
