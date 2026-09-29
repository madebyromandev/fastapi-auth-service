from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=1, max_length=128)

    model_config = ConfigDict(hide_input_in_errors=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class TokenPairResponse(TokenResponse):
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: SecretStr = Field(
        min_length=1,
        max_length=2048,
    )

    model_config = ConfigDict(hide_input_in_errors=True)