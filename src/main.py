from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select

from src.auth.router import router as auth_router
from src.config import ADMIN_EMAIL
from src.databse import AsyncSessionLocal, init_db
from src.document.router import router as document_router
from src.role import ensure_default_roles
from src.role.crud import RoleCrud
from src.role.router import router as role_router
from src.user.models import UserModel
from src.user.router import router as users_router

app = FastAPI()

Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def on_startup():
    await init_db()

    async with AsyncSessionLocal() as session:
        await ensure_default_roles(session)

        result = await session.execute(
            select(UserModel).where(UserModel.email == ADMIN_EMAIL)
        )
        admin = result.scalar_one_or_none()

        if admin:
            role_crud = RoleCrud(session)
            admin_role = await role_crud.get_by_name("admin")

            if admin_role not in admin.roles:
                admin.roles.append(admin_role)
                await session.commit()


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(role_router)
app.include_router(document_router)
