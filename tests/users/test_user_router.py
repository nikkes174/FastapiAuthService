import pytest

from src.role import RoleModel


@pytest.mark.asyncio
async def test_register_user_ok(
    client,
    override_get_db,
    db_session,
):
    db_session.add(RoleModel(name="user"))
    await db_session.commit()

    resp = await client.post(
        "/users/",
        json={
            "user_name": "test",
            "email": "test@mail.com",
            "password": "123",
        },
    )

    assert resp.status_code == 201
    assert resp.json()["email"] == "test@mail.com"


@pytest.mark.asyncio
async def test_register_user_exists(
    client,
    override_get_db,
    db_session,
):
    db_session.add(RoleModel(name="user"))
    await db_session.commit()

    await client.post(
        "/users/",
        json={
            "user_name": "test",
            "email": "test@mail.com",
            "password": "123",
        },
    )

    resp = await client.post(
        "/users/",
        json={
            "user_name": "test2",
            "email": "test@mail.com",
            "password": "123",
        },
    )

    assert resp.status_code == 400


import pytest

from src.auth.security import PasswordService
from src.user.models import UserModel


@pytest.mark.asyncio
async def test_profile_ok(
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

    override_current_user(user_1)

    resp = await client.get("/users/me")

    assert resp.status_code == 200
    assert resp.json()["email"] == "test@mail.com"


@pytest.mark.asyncio
async def test_profile_unauthorized(client):
    resp = await client.get("/users/me")
    assert resp.status_code == 401
