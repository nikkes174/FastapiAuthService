import pytest
from sqlalchemy import select

from src.auth.grafana_access.models import GrafanaAccessModel


@pytest.mark.asyncio
async def test_request_access_creates_pending(
    client,
    override_get_db,
    override_current_user,
    db_session,
    user_1,
):
    override_current_user(user_1)

    resp = await client.post("/auth/grafana/request-access")

    assert resp.status_code == 200
    assert resp.json()["status"] == "pending"

    result = await db_session.execute(select(GrafanaAccessModel))
    access = result.scalar_one()

    assert access.user_id == user_1["user_id"]
    assert access.status == "pending"
