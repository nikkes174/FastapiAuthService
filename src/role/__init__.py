from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.role.models import RoleModel


async def ensure_default_roles(session: AsyncSession):
    default_roles = {
        "user": "Роль пользователя по умолчанию",
        "admin": "Администратор системы",
    }

    for name, desc in default_roles.items():
        role = await session.scalar(
            select(RoleModel).where(RoleModel.name == name)
        )
        if not role:
            session.add(RoleModel(name=name, description=desc))

    await session.commit()
