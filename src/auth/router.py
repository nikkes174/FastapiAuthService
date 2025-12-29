from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt_service import ActionWithToken
from src.auth.schemas import TokenResponse
from src.auth.security import OAuth2PasswordRequestFormFixed, PasswordService
from src.auth.service import AuthService
from src.databse import get_db
from src.role.crud import RoleCrud
from src.user.crud import UserCrud

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(
    session: AsyncSession = Depends(get_db),
) -> AuthService:
    user_crud = UserCrud(session, PasswordService())
    role_crud = RoleCrud(session)

    return AuthService(
        user_crud=user_crud,
        security=PasswordService(),
        role=role_crud,
        token=ActionWithToken(),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestFormFixed = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        access_token, roles = await auth_service.login(
            email=form_data.username,
            password=form_data.password,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный email или пароль",
        )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        roles=roles,
    )
