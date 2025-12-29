from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.security import PasswordService
from src.databse import get_db
from src.user.crud import UserCrud
from src.user.models import UserModel
from src.user.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    description="Создаёт нового пользователя с ролью user",
    responses={
        201: {"description": "Пользователь создан"},
        400: {"description": "Пользователь уже существует"},
    },
)
async def create_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_db),
):
    user_crud = UserCrud(session, PasswordService())

    existing = await user_crud.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    user = await user_crud.create_user(data)

    return UserResponse.model_validate(user)


from uuid import UUID


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Профиль текущего пользователя",
)
async def profile(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        user_id = UUID(current_user["user_id"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = await session.get(UserModel, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return user
