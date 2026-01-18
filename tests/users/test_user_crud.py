import pytest

from src.auth.security import PasswordService
from src.role.models import RoleModel
from src.user.crud import UserCrud
from src.user.schemas import UserCreate


@pytest.mark.asyncio
async def test_create_user_ok(db_session):
    role = RoleModel(name="user")
    db_session.add(role)
    await db_session.commit()

    crud = UserCrud(db_session, PasswordService())

    data = UserCreate(
        user_name="test",
        email="test@mail.com",
        password="123",
    )

    user = await crud.create_user(data)

    assert user.id is not None
    assert user.email == "test@mail.com"


@pytest.mark.asyncio
async def test_create_user_without_default_role(db_session):
    crud = UserCrud(db_session, PasswordService())

    data = UserCreate(
        user_name="test",
        email="test@mail.com",
        password="123",
    )

    with pytest.raises(RuntimeError):
        await crud.create_user(data)


@pytest.mark.asyncio
async def test_get_by_email(db_session):
    role = RoleModel(name="user")
    db_session.add(role)
    await db_session.commit()

    crud = UserCrud(db_session, PasswordService())

    data = UserCreate(
        user_name="test",
        email="test@mail.com",
        password="123",
    )
    await crud.create_user(data)

    user = await crud.get_by_email("test@mail.com")
    assert user is not None
