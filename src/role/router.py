from fastapi import APIRouter, Depends

from src.auth.service import RoleService

router = APIRouter(prefix="/admin", tags=["Admin"])

admin_required = RoleService.require_role("admin")
staff_required = RoleService.require_any_role(["admin", "moderator"])


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
