import pytest
from fastapi import HTTPException

from src.auth.service import RoleService


def test_require_role_ok():
    checker = RoleService.require_role("admin")

    user = {
        "user_id": "1",
        "roles": ["admin"],
    }

    assert checker(user) == user


def test_require_role_forbidden():
    checker = RoleService.require_role("admin")

    user = {
        "user_id": "1",
        "roles": ["user"],
    }

    with pytest.raises(HTTPException) as exc:
        checker(user)

    assert exc.value.status_code == 403


def test_require_any_role_ok():
    checker = RoleService.require_any_role(["admin", "moderator"])

    user = {
        "user_id": "1",
        "roles": ["moderator"],
    }

    assert checker(user) == user


def test_require_any_role_forbidden():
    checker = RoleService.require_any_role(["admin", "moderator"])

    user = {
        "user_id": "1",
        "roles": ["user"],
    }

    with pytest.raises(HTTPException) as exc:
        checker(user)

    assert exc.value.status_code == 403


def test_can_access_resource_admin():
    user = {
        "user_id": "1",
        "roles": ["admin"],
    }

    assert RoleService.can_access_resource(user, owner_id="999") is True


def test_can_access_resource_owner():
    user = {
        "user_id": "42",
        "roles": ["user"],
    }

    assert RoleService.can_access_resource(user, owner_id="42") is True


def test_can_access_resource_forbidden():
    user = {
        "user_id": "1",
        "roles": ["user"],
    }

    assert RoleService.can_access_resource(user, owner_id="2") is False
