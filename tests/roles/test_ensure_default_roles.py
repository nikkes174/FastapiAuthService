import pytest
from sqlalchemy import select

from src.role import ensure_default_roles
from src.role.models import RoleModel


@pytest.mark.asyncio
async def test_ensure_default_roles_creates_roles(db_session):
    roles_before = (
        (await db_session.execute(select(RoleModel))).scalars().all()
    )
    assert roles_before == []

    await ensure_default_roles(db_session)

    roles_after = (await db_session.execute(select(RoleModel))).scalars().all()
    role_names = sorted(role.name for role in roles_after)

    assert role_names == ["admin", "user"]


@pytest.mark.asyncio
async def test_ensure_default_roles_idempotent(db_session):
    await ensure_default_roles(db_session)

    await ensure_default_roles(db_session)

    roles = (await db_session.execute(select(RoleModel))).scalars().all()
    role_names = sorted(role.name for role in roles)

    assert role_names == ["admin", "user"]
    assert len(roles) == 2
