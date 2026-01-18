import pytest
import pytest_asyncio
from sqlalchemy import select

from src.auth.security import PasswordService
from src.document.crud import DocumentCrud
from src.document.models import DocumentModel
from src.user.models import UserModel


@pytest_asyncio.fixture
async def user(db_session):
    user = UserModel(
        user_name="test",
        email="test@mail.com",
        password_hash=PasswordService.hash_password("123"),
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.mark.asyncio
async def test_document_create(db_session, user):
    crud = DocumentCrud(db_session)

    doc = await crud.create(
        title="Doc",
        user_id=user.id,
    )

    assert doc.id is not None
    assert doc.title == "Doc"
    assert doc.user_id == user.id


@pytest.mark.asyncio
async def test_get_by_id(db_session, user):
    crud = DocumentCrud(db_session)

    doc = await crud.create("Doc", user.id)

    found = await crud.get_by_id(doc.id)

    assert found is not None
    assert found.id == doc.id


@pytest.mark.asyncio
async def test_get_by_id_and_user_id(db_session, user):
    crud = DocumentCrud(db_session)

    doc = await crud.create("Doc", user.id)

    found = await crud.get_by_id_and_user_id(doc.id, user.id)

    assert found is not None
    assert found.id == doc.id


@pytest.mark.asyncio
async def test_get_by_id_and_user_id_not_owner(db_session, user):
    other_user = UserModel(
        user_name="other",
        email="other@mail.com",
        password_hash="x",
    )
    db_session.add(other_user)
    await db_session.commit()

    crud = DocumentCrud(db_session)
    doc = await crud.create("Doc", user.id)

    found = await crud.get_by_id_and_user_id(doc.id, other_user.id)

    assert found is None


from src.document.schemas import DocumentUpdate


@pytest.mark.asyncio
async def test_update_document(db_session, user):
    crud = DocumentCrud(db_session)
    doc = await crud.create("Old", user.id)

    updated = await crud.update(
        doc,
        DocumentUpdate(title="New"),
    )

    assert updated.title == "New"


@pytest.mark.asyncio
async def test_delete_document(db_session, user):
    crud = DocumentCrud(db_session)
    doc = await crud.create("To delete", user.id)

    await crud.delete(doc)

    result = await db_session.execute(
        select(DocumentModel).where(DocumentModel.id == doc.id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_search_by_title(db_session, user):
    crud = DocumentCrud(db_session)

    await crud.create("Hello world", user.id)
    await crud.create("Another", user.id)
    await crud.create("Hello again", user.id)

    results = await crud.search_by_title("Hello")

    titles = [d.title for d in results]

    assert len(results) == 2
    assert "Hello world" in titles
    assert "Hello again" in titles
