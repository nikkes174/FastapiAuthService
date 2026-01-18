import pytest
from sqlalchemy import select

from src.auth.security import PasswordService
from src.document.models import DocumentModel
from src.user.models import UserModel


@pytest.mark.asyncio
async def test_list_documents_requires_auth(client):
    resp = await client.get("/documents/")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_documents_ok(
    client,
    override_current_user,
    user_1,
):
    override_current_user(user_1)

    resp = await client.get("/documents/")
    assert resp.status_code == 200

    body = resp.json()
    assert body["message"] == "Список документов"
    assert body["current_user"]["id"] == str(user_1["user_id"])


@pytest.mark.asyncio
async def test_create_document_ok(
    client,
    override_get_db,
    override_current_user,
    db_session,
    user_1,
):
    # user в БД
    user = UserModel(
        id=user_1["user_id"],
        user_name="test",
        email="test@mail.com",
        password_hash=PasswordService.hash_password("123"),
    )
    db_session.add(user)
    await db_session.commit()

    override_current_user(user_1)

    resp = await client.post(
        "/documents/",
        json={"title": "My doc"},
    )

    assert resp.status_code == 201
    data = resp.json()

    assert data["title"] == "My doc"
    assert data["user_id"] == str(user_1["user_id"])


@pytest.mark.asyncio
async def test_update_document_owner_ok(
    client,
    override_get_db,
    override_current_user,
    db_session,
    user_1,
):
    user = UserModel(
        id=user_1["user_id"],
        user_name="test",
        email="test@mail.com",
        password_hash=PasswordService.hash_password("123"),
    )
    db_session.add(user)
    await db_session.commit()

    doc = DocumentModel(
        title="Before",
        user_id=user.id,
    )
    db_session.add(doc)
    await db_session.commit()

    override_current_user(user_1)

    resp = await client.put(
        f"/documents/{doc.id}",
        json={"title": "After"},
    )

    assert resp.status_code == 200
    assert resp.json()["title"] == "After"


@pytest.mark.asyncio
async def test_update_document_not_owner_forbidden(
    client,
    override_get_db,
    override_current_user,
    db_session,
    user_1,
    user_2,
):
    owner = UserModel(
        id=user_1["user_id"],
        user_name="owner",
        email="o@mail.com",
        password_hash="x",
    )
    db_session.add(owner)
    await db_session.commit()

    doc = DocumentModel(
        title="Secret",
        user_id=owner.id,
    )
    db_session.add(doc)
    await db_session.commit()

    override_current_user(user_2)

    resp = await client.put(
        f"/documents/{doc.id}",
        json={"title": "Hack"},
    )

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_document_owner_ok(
    client,
    override_get_db,
    override_current_user,
    db_session,
    user_1,
):
    user = UserModel(
        id=user_1["user_id"],
        user_name="test",
        email="test@mail.com",
        password_hash="x",
    )
    db_session.add(user)
    await db_session.commit()

    doc = DocumentModel(
        title="To delete",
        user_id=user.id,
    )
    db_session.add(doc)
    await db_session.commit()

    override_current_user(user_1)

    resp = await client.delete(f"/documents/{doc.id}")

    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"

    result = await db_session.execute(
        select(DocumentModel).where(DocumentModel.id == doc.id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_document_not_owner_forbidden(
    client,
    override_get_db,
    override_current_user,
    db_session,
    user_1,
    user_2,
):
    owner = UserModel(
        id=user_1["user_id"],
        user_name="owner",
        email="o@mail.com",
        password_hash="x",
    )
    db_session.add(owner)
    await db_session.commit()

    doc = DocumentModel(
        title="Secret",
        user_id=owner.id,
    )
    db_session.add(doc)
    await db_session.commit()

    override_current_user(user_2)

    resp = await client.delete(f"/documents/{doc.id}")

    assert resp.status_code == 403
    assert resp.json()["detail"] == "Access denied"
