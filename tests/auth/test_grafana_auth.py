
import pytest

from src.auth.grafana_access.models import GrafanaAccessModel
from src.auth.security import PasswordService
from src.user.models import UserModel


@pytest.mark.asyncio
async def test_grafana_admin_allowed(
    client,
    override_current_user,
    admin,
):
    override_current_user(admin)

    resp = await client.get("/auth/grafana")

    assert resp.status_code == 200
    assert "X-WEBAUTH-USER" in resp.headers


@pytest.mark.asyncio
async def test_grafana_user_without_access_forbidden(
    client,
    override_get_db,
    override_current_user,
    user_1,
):
    override_current_user(user_1)

    resp = await client.get("/auth/grafana")

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_grafana_user_pending_forbidden(
    client,
    override_get_db,
    override_current_user,
    db_session,
    user_1,
):
    user = UserModel(
        id=user_1["user_id"],
        user_name="u",
        email="u@mail.com",
        password_hash=PasswordService.hash_password("123"),
    )
    db_session.add(user)
    db_session.add(GrafanaAccessModel(user_id=user.id, status="pending"))
    await db_session.commit()

    override_current_user(user_1)

    resp = await client.get("/auth/grafana")

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_grafana_user_approved_allowed(
    client,
    override_get_db,
    override_current_user,
    db_session,
    user_1,
):
    user = UserModel(
        id=user_1["user_id"],
        user_name="u",
        email="u@mail.com",
        password_hash=PasswordService.hash_password("123"),
    )
    db_session.add(user)
    db_session.add(GrafanaAccessModel(user_id=user.id, status="approved"))
    await db_session.commit()

    override_current_user(user_1)

    resp = await client.get("/auth/grafana")

    assert resp.status_code == 200
    assert "X-WEBAUTH-USER" in resp.headers
