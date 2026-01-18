import pytest
from fastapi import HTTPException, Request
from starlette.datastructures import Headers

from src.auth.dependencies import get_current_user
from src.auth.jwt_service import ActionWithToken


def make_request_with_cookie(token: str | None):
    headers = {}
    if token:
        headers["cookie"] = f"access_token={token}"

    return Request(
        scope={
            "type": "http",
            "headers": Headers(headers).raw,
        }
    )


def test_get_current_user_invalid_token(monkeypatch):
    def fake_decode(token: str):
        raise ValueError("invalid")

    monkeypatch.setattr(
        ActionWithToken,
        "decode_access_token",
        fake_decode,
    )

    request = make_request_with_cookie("bad.token")

    with pytest.raises(HTTPException) as exc:
        get_current_user(request)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid or expired token"


def test_get_current_user_missing_sub(monkeypatch):
    def fake_decode(token: str):
        return {
            # "sub" отсутствует
            "roles": ["user"],
        }

    monkeypatch.setattr(
        ActionWithToken,
        "decode_access_token",
        fake_decode,
    )

    request = make_request_with_cookie("valid.token")

    with pytest.raises(HTTPException) as exc:
        get_current_user(request)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token payload"


def test_get_current_user_missing_roles_defaults_to_empty(monkeypatch):
    def fake_decode(token: str):
        return {
            "sub": "123",
        }

    monkeypatch.setattr(
        ActionWithToken,
        "decode_access_token",
        fake_decode,
    )

    request = make_request_with_cookie("valid.token")

    user = get_current_user(request)

    assert user["id"] == "123"
    assert user["roles"] == []
