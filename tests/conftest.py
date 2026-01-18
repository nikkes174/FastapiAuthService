import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.auth.dependencies import get_current_user
from src.databse import Base, get_db
from src.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture()
def user_1():
    return {"user_id": uuid.uuid4(), "roles": ["user"]}


@pytest.fixture()
def user_2():
    return {"user_id": uuid.uuid4(), "roles": ["user"]}


@pytest.fixture()
def admin():
    return {"user_id": uuid.uuid4(), "roles": ["admin"]}


@pytest.fixture
def override_current_user():
    def _set(user):
        fixed = {
            "id": user["user_id"],
            "roles": user["roles"],
            "email": user.get("email", "test@mail.com"),
            "user_name": user.get("user_name"),
        }
        app.dependency_overrides[get_current_user] = lambda: fixed

    yield _set
    app.dependency_overrides.pop(get_current_user, None)


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    async_session_factory = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session


@pytest.fixture
def override_get_db(db_session):
    async def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac
