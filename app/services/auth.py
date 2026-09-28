from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas.auth import LoginRequest

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate

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

