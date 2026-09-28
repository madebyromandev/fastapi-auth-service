from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=15, max_length=128)

    model_config = ConfigDict(hide_input_in_errors=True)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)