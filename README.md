# Auth Service API

Backend-сервис регистрации и аутентификации пользователей на FastAPI.

Проект реализует вход по email и паролю, выдачу JWT access- и refresh-токенов, ротацию refresh-токенов и получение профиля авторизованного пользователя. Данные хранятся в PostgreSQL, изменения схемы управляются через Alembic.

## Live Demo

[Открыть Swagger UI](https://fastapi-auth-service-production-0cc1.up.railway.app/docs)

## Возможности

- Регистрация пользователей с проверкой уникальности email.
- Хеширование паролей с помощью Argon2.
- Вход по email и паролю.
- JWT access-токены для доступа к защищённым маршрутам.
- Refresh-токены с ротацией: после обновления использованный токен отзывается.
- Хранение SHA-256 хешей refresh-токенов в базе данных.
- Получение профиля через защищённый endpoint `/users/me`.
- Проверка срока действия и типа токена.
- Валидация входных данных без возврата паролей в сообщениях об ошибках.
- Миграции базы данных и деплой на Railway.

## Стек

Python · FastAPI · PostgreSQL · SQLAlchemy · Alembic ·
Pydantic Settings · PyJWT · pwdlib / Argon2 · psycopg · Uvicorn · Railway

## API

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/health` | Проверка работы приложения |
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Получение пары токенов |
| POST | `/auth/refresh` | Обновление пары токенов |
| GET | `/users/me` | Профиль авторизованного пользователя |

Регистрация и вход принимают JSON с полями `email` и `password`.
Пароль при регистрации должен содержать от 15 до 128 символов.

## Как проверить через Swagger

1. Зарегистрируйте пользователя через `POST /auth/register`.
2. Выполните `POST /auth/login` с теми же данными.
3. Скопируйте значение `access_token`.
4. Нажмите **Authorize** и вставьте токен без кавычек и без слова `Bearer`.
5. Выполните `GET /users/me` — сервер вернёт профиль пользователя.
6. Передайте `refresh_token` в `POST /auth/refresh` — сервер выдаст новую пару токенов.
7. Повторите запрос с прежним refresh-токеном — сервер вернёт `401`.

Для последующего обновления используйте новый refresh-токен из последнего ответа.

## Структура проекта

- `app/main.py` — создание приложения и подключение маршрутов.
- `app/core/` — настройки, подключение к БД, работа с токенами и зависимости.
- `app/models/` — SQLAlchemy-модели пользователей и refresh-токенов.
- `app/schemas/` — Pydantic-схемы запросов и ответов.
- `app/services/` — логика регистрации, входа и ротации токенов.
- `app/routers/` — HTTP-маршруты.
- `alembic/` — миграции базы данных.

## Локальный запуск

Нужны Python 3.10+, PostgreSQL и Git.
Команды ниже предназначены для Windows PowerShell.

### 1. Клонировать репозиторий

```powershell
git clone https://github.com/madebyromandev/fastapi-auth-service.git
cd fastapi-auth-service
```

### 2. Создать виртуальное окружение и установить зависимости

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. Подготовить PostgreSQL

Выполните в psql под администратором PostgreSQL, указав собственный пароль:

```sql
CREATE USER auth_user WITH PASSWORD 'replace_with_your_password';
CREATE DATABASE auth_service OWNER auth_user;
```

### 4. Настроить окружение

Скопируйте пример настроек:

```powershell
Copy-Item .env.example .env
```

Укажите в `.env` параметры своей базы:

```dotenv
APP_NAME="Auth Service API Local"
DB_HOST=localhost
DB_PORT=5432
DB_NAME=auth_service
DB_USER=auth_user
DB_PASSWORD=replace_with_your_password

JWT_SECRET_KEY=replace_with_generated_secret_key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

Сгенерируйте секретный ключ:

```powershell
python -c "import secrets; print(secrets.token_hex(32))" | Set-Clipboard
```

Вставьте содержимое буфера обмена в значение `JWT_SECRET_KEY`.

Вместо отдельных параметров `DB_*` можно задать `DATABASE_URL`.
Если он указан, приложение использует его в первую очередь.

Файл `.env` не должен попадать в Git.

### 5. Применить миграции

```powershell
python -m alembic upgrade head
```

### 6. Запустить API

```powershell
python -m uvicorn app.main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

## Деплой на Railway

Приложение и PostgreSQL работают как отдельные сервисы.

Переменные приложения:

- `DATABASE_URL` — ссылка на переменную базы: `${{Postgres.DATABASE_URL}}`.
- `JWT_SECRET_KEY` — отдельный случайный секретный ключ.

Сроки действия токенов по умолчанию: access — 15 минут, refresh — 7 дней.
Их можно изменить через `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` и
`JWT_REFRESH_TOKEN_EXPIRE_DAYS`.

**Pre-Deploy Command:**

```bash
python -m alembic upgrade head
```

**Start Command:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Проверенные сценарии

Проверено вручную через Swagger UI, в том числе после деплоя на Railway:

| Сценарий | Результат |
|---|---|
| Регистрация нового пользователя | `201` |
| Вход с верными данными | `200`, пара токенов |
| Получение профиля с действующим access-токеном | `200` |
| Запрос профиля с истёкшим access-токеном | `401` |
| Обновление по действующему refresh-токену | `200`, новая пара |
| Повторное использование прежнего refresh-токена | `401` |

## Ограничения и дальнейшее развитие

Учебный проект для портфолио. Пока не реализованы:

- Подтверждение email и восстановление пароля.
- Ограничение частоты попыток входа.
- Выход с отзывом refresh-токена и управление сессиями.
- Отзыв всей цепочки токенов при повторном использовании старого refresh-токена.
- Автоматические тесты.