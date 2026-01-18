from typing import Optional

from fastapi import Form
from passlib.context import CryptContext

pwd = CryptContext(schemes=["argon2"], deprecated="auto")


class PasswordService:

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return pwd.verify(password, hashed)


class OAuth2PasswordRequestFormFixed:
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        grant_type: Optional[str] = Form(None),
        scope: str = Form(""),
        client_id: Optional[str] = Form(None),
        client_secret: Optional[str] = Form(None),
    ):
        self.username = username
        self.password = password
