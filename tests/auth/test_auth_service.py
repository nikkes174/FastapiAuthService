from datetime import datetime, timedelta

import jwt
import pytest
import pytest_asyncio

from src.auth.jwt_service import ActionWithToken
from src.auth.security import PasswordService
from src.auth.service import AuthService
from src.config import JWT_ALGORITHM, JWT_SECRET_KEY
from src.role.crud import RoleCrud
from src.role.models import RoleModel
from src.user.crud import UserCrud
from src.user.models import UserModel


@pytest_asyncio.fixture
async def auth_service(db_session):
    db_session.add(RoleModel(name="user"))
    db_session.add(RoleModel(name="admin"))
    await db_session.commit()

    return AuthService(
        user_crud=UserCrud(db_session, PasswordService()),
        security=PasswordService(),
        role=RoleCrud(db_session),
        token=ActionWithToken(),
    )


@pytest.mark.asyncio
async def test_login_user_not_found_real(auth_service, caplog):
    with caplog.at_level("WARNING"):
        with pytest.raises(ValueError):
            await auth_service.login("no@mail.com", "123")

    assert "пользователь не найден" in caplog.text.lower()


from src.user.schemas import UserCreate


@pytest.mark.asyncio
async def test_login_wrong_password_real(auth_service, db_session, caplog):
    user_crud = auth_service.user_crud

    await user_crud.create_user(
        UserCreate(
            user_name="test",
            email="test@mail.com",
            password="correct",
        )
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(ValueError):
            await auth_service.login("test@mail.com", "wrong")

    assert "неправильный пароль" in caplog.text.lower()


@pytest.mark.asyncio
async def test_login_success_real(auth_service, db_session, caplog):
    user_crud = auth_service.user_crud

    user = await user_crud.create_user(
        UserCreate(
            user_name="admin",
            email="admin@mail.com",
            password="123",
        )
    )

    role = await auth_service.role.get_by_name("admin")

    await db_session.execute(
        UserModel.roles.property.secondary.insert().values(
            user_id=user.id,
            role_id=role.id,
        )
    )
    await db_session.commit()

    with caplog.at_level("INFO"):
        token, roles = await auth_service.login("admin@mail.com", "123")

    assert isinstance(token, str)
    assert "admin" in roles
    assert "успешный вход" in caplog.text.lower()


def test_decode_expired_token():
    token = jwt.encode(
        {
            "sub": "123",
            "roles": ["user"],
            "exp": datetime.utcnow() - timedelta(minutes=1),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(ValueError) as exc:
        ActionWithToken.decode_access_token(token)

    assert "expired" in str(exc.value).lower()
