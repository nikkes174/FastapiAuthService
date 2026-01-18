import pytest

from src.auth.jwt_service import ActionWithToken


def test_create_and_decode_token():
    token = ActionWithToken.create_access_token(
        user_id="123",
        roles=["admin"],
    )

    payload = ActionWithToken.decode_access_token(token)

    assert payload["sub"] == "123"
    assert payload["roles"] == ["admin"]


def test_decode_invalid_token():
    with pytest.raises(ValueError):
        ActionWithToken.decode_access_token("invalid.token")
