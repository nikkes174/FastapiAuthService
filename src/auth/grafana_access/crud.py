from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.grafana_access.models import GrafanaAccessModel


class GrafanaAccessCrud:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: UUID) -> GrafanaAccessModel | None:
        return await self.session.get(GrafanaAccessModel, user_id)

    async def request(self, user_id: UUID) -> GrafanaAccessModel:
        access = GrafanaAccessModel(user_id=user_id, status="pending")
        self.session.add(access)
        await self.session.commit()
        return access

    async def approve(self, user_id: UUID) -> None:
        access = await self.get(user_id)
        if access:
            access.status = "approved"
            await self.session.commit()

    async def reject(self, user_id: UUID) -> None:
        access = await self.get(user_id)
        if access:
            access.status = "rejected"
            await self.session.commit()
