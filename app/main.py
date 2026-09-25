from fastapi import FastAPI

app = FastAPI(
    title="Auth Service API",
    description="API для регистрации и авторизации пользователей",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}