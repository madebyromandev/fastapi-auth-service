from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


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