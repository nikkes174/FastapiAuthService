import pytest
from fastapi import HTTPException

from src.depends import admin_required, staff_required


def test_admin_required_ok():
    user = {
        "user_id": "1",
        "roles": ["admin"],
    }

    result = admin_required(user)

    assert result == user


def test_admin_required_forbidden():
    user = {
        "user_id": "1",
        "roles": ["user"],
    }

    with pytest.raises(HTTPException) as exc:
        admin_required(user)

    assert exc.value.status_code == 403


def test_staff_required_admin_ok():
    user = {
        "user_id": "1",
        "roles": ["admin"],
    }

    assert staff_required(user) == user


def test_staff_required_forbidden():
    user = {
        "user_id": "1",
        "roles": ["user"],
    }

    with pytest.raises(HTTPException) as exc:
        staff_required(user)

    assert exc.value.status_code == 403
