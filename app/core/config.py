from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Auth Service API"

    database_url: SecretStr | None = None

    db_host: str | None = None
    db_port: int = 5432
    db_name: str | None = None
    db_user: str | None = None
    db_password: SecretStr | None = None

    jwt_secret_key: SecretStr
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        hide_input_in_errors=True,
    )


settings = Settings()