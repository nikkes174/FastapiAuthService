from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.databse import get_db
from src.depends import admin_required, staff_required
from src.role.crud import RoleCrud
from src.user.crud import UserCrud

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/make-admin")
async def make_admin(
    email: str,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    if "admin" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    user_crud = UserCrud(session)
    role_crud = RoleCrud(session)

    user = await user_crud.get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = await role_crud.get_by_name("admin")
    if not role:
        raise HTTPException(status_code=500, detail="Admin role missing")

    if role in user.roles:
        return {"status": "already admin"}

    user.roles.append(role)
    await session.commit()

    return {"status": "ok", "email": email}


@router.get(
    "/only",
    summary="Доступ только для администратора",
    description="Эндпоинт доступен исключительно пользователям с ролью admin",
)
async def admin_endpoint(
    current_user=Depends(admin_required),
):
    return {"message": "Привет админ!"}


@router.get(
    "/staff",
    summary="Доступ для администраторов и модераторов",
    description="Эндпоинт доступен пользователям с ролями admin или moderator",
)
async def staff_endpoint(
    current_user=Depends(staff_required),
):
    return {"message": "Привет"}
