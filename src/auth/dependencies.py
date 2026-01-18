from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.auth.jwt_service import ActionWithToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


from fastapi import Request


def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = ActionWithToken.decode_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    roles = payload.get("roles", [])

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return {
        "id": user_id,
        "roles": roles,
        "email": payload.get("email"),  # если есть
        "user_name": payload.get("user_name"),  # если есть
    }
