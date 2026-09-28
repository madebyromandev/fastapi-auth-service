from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routers.users import router as users_router

from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router


app = FastAPI(
    title=settings.app_name,
    description="API для регистрации и авторизации пользователей",
    version="0.1.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = [
        {
            "type": error["type"],
            "loc": error["loc"],
            "msg": error["msg"],
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)