from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from uuid import uuid4
from hashlib import sha256
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        ),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )

def get_user_id_from_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "type", "iat", "exp"]},
        )

        if payload["type"] != "access":
            return None

        user_id = int(payload["sub"])

        if user_id <= 0:
            return None

        return user_id

    except (InvalidTokenError, ValueError, TypeError):
        return None

def create_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + timedelta(
            days=settings.jwt_refresh_token_expire_days
        ),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )

def hash_refresh_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()

def decode_refresh_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={
                "require": ["sub", "type", "jti", "iat", "exp"]
            },
        )

        if payload["type"] != "refresh":
            return None

        if int(payload["sub"]) <= 0:
            return None

        if not isinstance(payload["jti"], str) or not payload["jti"]:
            return None

        return payload

    except (InvalidTokenError, ValueError, TypeError):
        return None