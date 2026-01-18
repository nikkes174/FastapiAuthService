import pytest
import pytest_asyncio

from src.auth.grafana_access.crud import GrafanaAccessCrud
from src.auth.security import PasswordService
from src.user.models import UserModel


@pytest_asyncio.fixture
async def user(db_session):
    user = UserModel(
        user_name="user",
        email="user@mail.com",
        password_hash=PasswordService.hash_password("123"),
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.mark.asyncio
async def test_request_access_creates_pending(db_session, user):
    crud = GrafanaAccessCrud(db_session)

    access = await crud.request(user.id)

    assert access.user_id == user.id
    assert access.status == "pending"


@pytest.mark.asyncio
async def test_get_access(db_session, user):
    crud = GrafanaAccessCrud(db_session)
    await crud.request(user.id)

    access = await crud.get(user.id)

    assert access is not None
    assert access.user_id == user.id


@pytest.mark.asyncio
async def test_approve_access(db_session, user):
    crud = GrafanaAccessCrud(db_session)
    await crud.request(user.id)

    await crud.approve(user.id)

    access = await crud.get(user.id)
    assert access.status == "approved"


@pytest.mark.asyncio
async def test_reject_access(db_session, user):
    crud = GrafanaAccessCrud(db_session)
    await crud.request(user.id)

    await crud.reject(user.id)

    access = await crud.get(user.id)
    assert access.status == "rejected"
