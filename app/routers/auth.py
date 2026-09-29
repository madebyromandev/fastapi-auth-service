from app.schemas.auth import LoginRequest, TokenPairResponse
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import authenticate_user
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.auth import EmailAlreadyExistsError, register_user
from sqlalchemy.exc import SQLAlchemyError
from app.services.auth import create_token_pair

from app.schemas.auth import RefreshRequest
from app.services.auth import (
    InvalidRefreshTokenError,
    rotate_refresh_token,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        return register_user(db, data)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None

@router.post("/login", response_model=TokenPairResponse)
def login(
    data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenPairResponse:
    user = authenticate_user(db, data)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        tokens = create_token_pair(db, user.id)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return tokens

@router.post("/refresh", response_model=TokenPairResponse)
def refresh(
    data: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenPairResponse:
    try:
        tokens = rotate_refresh_token(
            db,
            data.refresh_token.get_secret_value(),
        )
        db.commit()

    except InvalidRefreshTokenError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from None

    except SQLAlchemyError:
        db.rollback()
        raise

    return tokens