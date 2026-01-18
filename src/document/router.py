from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.databse import get_db
from src.document.crud import DocumentCrud
from src.document.schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/", summary="Получить список документов")
async def list_documents(
    current_user=Depends(get_current_user),
):
    return {
        "message": "Список документов",
        "current_user": current_user,
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document_crud = DocumentCrud(session)
    document = await document_crud.get_by_id(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    current_user_id = current_user["id"]

    if (
        "admin" not in current_user["roles"]
        and document.user_id != current_user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    await document_crud.delete(document)
    return {"status": "deleted"}


@router.put(
    "/{document_id}",
    summary="Обновить документ",
    description=(
        "Обновляет данные документа. "
        "Доступ разрешён владельцу документа или пользователю с ролью admin."
    ),
    responses={
        200: {"description": "Документ успешно обновлён"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Документ не найден"},
    },
)
async def update_document(
    document_id: UUID,
    data: DocumentUpdate,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document_crud = DocumentCrud(session)

    is_admin = "admin" in current_user["roles"]

    if not is_admin:
        document = await document_crud.get_by_id_and_user_id(
            document_id=document_id,
            user_id=current_user["id"],
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

    else:
        document = await document_crud.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

    updated_document = await document_crud.update(document, data)
    return updated_document


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать документ",
    description="Создаёт документ, принадлежащий текущему пользователю",
    responses={
        200: {"description": "Документ успешно обновлён"},
        401: {"description": "Неавторизован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Документ не найден"},
    },
)
async def create_document(
    data: DocumentCreate,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document_crud = DocumentCrud(session)

    user_id = current_user["id"]

    document = await document_crud.create(
        title=data.title,
        user_id=user_id,
    )
    return document
