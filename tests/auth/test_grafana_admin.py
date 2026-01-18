import pytest
from sqlalchemy import select

from src.auth.grafana_access.models import GrafanaAccessModel


@pytest.mark.asyncio
async def test_admin_can_approve(
    client,
    override_get_db,
    override_current_user,
    db_session,
    admin,
    user_1,
):
    override_current_user(admin)

    db_session.add(
        GrafanaAccessModel(user_id=user_1["user_id"], status="pending")
    )
    await db_session.commit()

    resp = await client.post(
        f"/auth/admin/grafana/approve?user_id={user_1['user_id']}"
    )

    assert resp.status_code == 200

    result = await db_session.execute(select(GrafanaAccessModel))
    access = result.scalar_one()

    assert access.status == "approved"


@pytest.mark.asyncio
async def test_non_admin_cannot_approve(
    client,
    override_current_user,
    user_1,
):
    override_current_user(user_1)

    resp = await client.post(
        f"/auth/admin/grafana/approve?user_id={user_1['user_id']}"
    )

    assert resp.status_code == 403
