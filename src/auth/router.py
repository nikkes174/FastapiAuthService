from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.grafana_access.crud import GrafanaAccessCrud
from src.auth.jwt_service import ActionWithToken
from src.auth.security import PasswordService
from src.auth.service import AuthService
from src.databse import get_db
from src.depends import admin_required
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


from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm


@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
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

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
    )

    return {
        "detail": "Logged in",
        "roles": roles,
    }


@router.get("/grafana")
async def grafana_auth(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    roles = user["roles"]

    if "admin" in roles:
        allowed = True
    else:
        crud = GrafanaAccessCrud(session)
        access = await crud.get(user_id=user["id"])
        allowed = access is not None and access.status == "approved"

    if not allowed:
        raise HTTPException(status_code=403)

    return Response(
        headers={
            "X-WEBAUTH-USER": user["email"],
        }
    )


@router.post("/grafana/request-access")
async def request_grafana_access(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    crud = GrafanaAccessCrud(session)
    await crud.request(user_id=user["id"])
    return {"status": "pending"}


@router.post("/admin/grafana/approve")
async def approve_grafana(
    user_id: UUID,
    current_user=Depends(admin_required),
    session: AsyncSession = Depends(get_db),
):
    await GrafanaAccessCrud(session).approve(user_id)
    return {"status": "approved"}
