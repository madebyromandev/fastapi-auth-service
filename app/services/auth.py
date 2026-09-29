from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas.auth import LoginRequest

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate

from datetime import datetime, timezone

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_refresh_token,
)
from app.models.refresh_token import RefreshToken
from app.schemas.auth import TokenPairResponse

DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing")

class EmailAlreadyExistsError(Exception):
    pass


def register_user(db: Session, data: UserCreate) -> User:
    user = User(
        email=str(data.email).lower(),
        hashed_password=hash_password(
            data.password.get_secret_value()
        ),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        if (
            isinstance(exc.orig, UniqueViolation)
            and exc.orig.diag.constraint_name == "users_email_key"
        ):
            raise EmailAlreadyExistsError(
                "Email already registered"
            ) from None

        raise

    db.refresh(user)
    return user

def authenticate_user(db: Session, data: LoginRequest) -> User | None:
    email = str(data.email).lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    hashed_password = (
        user.hashed_password
        if user is not None
        else DUMMY_PASSWORD_HASH
    )

    password_is_valid = verify_password(
        data.password.get_secret_value(),
        hashed_password,
    )

    if user is None or not password_is_valid:
        return None

    return user


def create_token_pair(
    db: Session,
    user_id: int,
) -> TokenPairResponse:
    refresh_token = create_refresh_token(user_id)
    payload = decode_refresh_token(refresh_token)

    if payload is None:
        raise RuntimeError("Could not create refresh token")

    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=datetime.fromtimestamp(
                payload["exp"],
                tz=timezone.utc,
            ),
        )
    )

    return TokenPairResponse(
        access_token=create_access_token(user_id),
        refresh_token=refresh_token,
    )


class InvalidRefreshTokenError(Exception):
    pass


def rotate_refresh_token(
    db: Session,
    token: str,
) -> TokenPairResponse:
    payload = decode_refresh_token(token)

    if payload is None:
        raise InvalidRefreshTokenError()

    stored_token = db.scalar(
        select(RefreshToken)
        .where(
            RefreshToken.token_hash == hash_refresh_token(token)
        )
        .with_for_update()
    )

    now = datetime.now(timezone.utc)

    if (
        stored_token is None
        or stored_token.revoked_at is not None
        or stored_token.expires_at <= now
        or stored_token.user_id != int(payload["sub"])
    ):
        raise InvalidRefreshTokenError()

    user = db.get(User, stored_token.user_id)

    if user is None:
        raise InvalidRefreshTokenError()

    stored_token.revoked_at = now

    return create_token_pair(db, user.id)

