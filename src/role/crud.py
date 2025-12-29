from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.role.models import RoleModel


class RoleCrud:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> RoleModel | None:
        stmt = select(RoleModel).where(RoleModel.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
