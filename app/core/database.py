from collections.abc import Generator

from sqlalchemy import URL, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


if settings.database_url is not None:
    try:
        database_url = make_url(
            settings.database_url.get_secret_value()
        )
    except (ArgumentError, ValueError):
        raise ValueError("Invalid DATABASE_URL format") from None

    if database_url.get_backend_name() not in {
        "postgres",
        "postgresql",
    }:
        raise ValueError("DATABASE_URL must use PostgreSQL")

    database_url = database_url.set(
        drivername="postgresql+psycopg"
    )

else:
    if (
        not settings.db_host
        or not settings.db_name
        or not settings.db_user
        or settings.db_password is None
    ):
        raise ValueError(
            "Set DATABASE_URL or all required DB_* settings"
        )

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password.get_secret_value(),
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


engine = create_engine(
    database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session