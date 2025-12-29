from datetime import datetime, timedelta
from typing import List

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from src.config import JWT_ALGORITHM, JWT_SECRET_KEY, LIFETIME_TOKEN


class ActionWithToken:

    @staticmethod
    def create_access_token(
        *,
        user_id: str,
        roles: List[str],
    ) -> str:
        payload = {
            "sub": user_id,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(minutes=LIFETIME_TOKEN),
        }

        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
            )
        except ExpiredSignatureError:
            raise ValueError("Token expired")
        except InvalidTokenError:
            raise ValueError("Invalid token")
