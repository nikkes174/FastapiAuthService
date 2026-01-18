from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import PasswordService
from src.role.crud import RoleCrud
from src.role.models import UserRoleModel
from src.user.models import UserModel
from src.user.schemas import UserCreate


class UserCrud:
    def __init__(self, session: AsyncSession, security: PasswordService):
        self.session = session
        self.security = security

    async def create_user(self, data: UserCreate) -> UserModel:
        user = UserModel(
            user_name=data.user_name,
            email=data.email,
            password_hash=self.security.hash_password(data.password),
        )

        self.session.add(user)
        await self.session.flush()  # user.id получен

        role = await RoleCrud(self.session).get_by_name("user")
        if not role:
            raise RuntimeError("Default role 'user' not found")

        self.session.add(
            UserRoleModel(
                user_id=user.id,
                role_id=role.id,
            )
        )

        await self.session.commit()
        return user

    async def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
