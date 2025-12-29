from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.databse import AsyncSessionLocal, init_db
from src.document.router import router as document_router
from src.role import ensure_default_roles
from src.role.router import router as role_router
from src.user.router import router as users_router

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()

    async with AsyncSessionLocal() as session:
        await ensure_default_roles(session)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(role_router)
app.include_router(document_router)
