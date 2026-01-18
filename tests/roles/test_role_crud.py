import pytest

from src.role.crud import RoleCrud
from src.role.models import RoleModel


@pytest.mark.asyncio
async def test_get_by_name_returns_role(db_session):
    role = RoleModel(name="admin", description="Admin role")
    db_session.add(role)
    await db_session.commit()

    crud = RoleCrud(db_session)

    found = await crud.get_by_name("admin")

    assert found is not None
    assert found.name == "admin"


@pytest.mark.asyncio
async def test_get_by_name_returns_none_if_missing(db_session):
    crud = RoleCrud(db_session)

    role = await crud.get_by_name("missing")

    assert role is None
