from fastapi import FastAPI

from app.core.config import settings
from app.routers.health import router as health_router

app = FastAPI(
    title=settings.app_name,
    description="API для регистрации и авторизации пользователей",
    version="0.1.0",
)

app.include_router(health_router)