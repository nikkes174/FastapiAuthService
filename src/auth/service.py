import logging

from fastapi import Depends, HTTPException, status

from src.auth.dependencies import get_current_user
from src.auth.jwt_service import ActionWithToken
from src.auth.security import PasswordService
from src.role.crud import RoleCrud
from src.user.crud import UserCrud

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        user_crud: UserCrud,
        security: PasswordService,
        role: RoleCrud,
        token: ActionWithToken,
    ):
        self.user_crud = user_crud
        self.security = security
        self.role = role
        self.token = token

    async def login(self, email: str, password: str) -> tuple[str, list[str]]:
        logger.info("Login attempt", extra={"email": email})

        user = await self.user_crud.get_by_email(email)

        if not user:
            logger.warning(
                "Не удалось войти: пользователь не найден",
                extra={"email": email},
            )
            raise ValueError("Пользователя не существует")

        password_ok = self.security.verify_password(
            password, user.password_hash
        )
        if not password_ok:
            logger.warning(
                "Не удаловь войти: неправильный пароль",
                extra={"email": email, "user_id": str(user.id)},
            )
            raise ValueError("Неверный пароль")

        roles = [role.name for role in user.roles]
        logger.info(
            "Успешный вход",
            extra={"email": email, "user_id": str(user.id), "roles": roles},
        )

        access_token = self.token.create_access_token(
            user_id=str(user.id),
            roles=roles,
        )

        return access_token, roles


class RoleService:

    @staticmethod
    def require_role(required_role: str):
        def checker(
            current_user: dict = Depends(get_current_user),
        ):
            if required_role not in current_user.get("roles", []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав доступа",
                )
            return current_user

        return checker

    @staticmethod
    def require_any_role(required_roles: list[str]):
        def checker(
            current_user: dict = Depends(get_current_user),
        ):
            if not any(
                role in current_user.get("roles", [])
                for role in required_roles
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав доступа",
                )
            return current_user

        return checker

    @staticmethod
    def can_access_resource(current_user: dict, owner_id: str) -> bool:
        return "admin" in current_user["roles"] or current_user[
            "user_id"
        ] == str(owner_id)
