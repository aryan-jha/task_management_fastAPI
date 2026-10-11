# FastAPI learning journey

What this repo actually covers. Empty stubs and migrations are ignored.

## 1. FastAPI basics (`progress.txt`)

- Creating a `FastAPI()` app
- Running with Uvicorn (`--reload`) and a venv
- GET / POST / PUT routes
- Path parameters (`/about/{userId}`)
- Query parameters (`page`, `limit`, `search`)
- Request bodies with Pydantic
- Nested models (`fullDetail` wrapping `User`)
- `response_model`
- `status_code`
- `HTTPException`
- Raw `Request` object (`body`, `query_params`)
- In-memory list as a fake database
- Sync and async handlers

## 2. Project layout

- `app/main.py` — app entry, router mounting
- `app/core/config.py` — settings
- `app/database/connection.py` — DB engine/session
- `app/modules/users/` and `app/modules/tasks/` — feature modules
- `app/common/utils.py` — shared auth + email helpers
- Router → service → repository → model. `schema.py` is the request/response contract.

## 3. Routing and HTTP API design

- `APIRouter` with prefixes (`/user`, `/tasks`)
- `app.include_router(...)`
- Full CRUD on tasks: create, list, get-by-id, update, delete
- User register / login / is_authenticated
- Path params for IDs (`/{taskId}`)
- `status.HTTP_*` constants (`200`, `201`, `400`, `401`, `403`, `404`)
- `response_model` on user endpoints so hashed passwords are not leaked

## 4. Pydantic (request/response contracts)

- Separate input vs output schemas (`UserSchema` vs `UserPublicSchema`)
- Wrapper response models (`status`, `message`, `data`)
- `ConfigDict(from_attributes=True)` so ORM objects can be returned
- `model_validate()` and `model_dump()`
- Default field values (`is_completed: bool = False`)
- Typing like `list[Users]`, `Annotated[...]`

Not used yet: `Field(...)` constraints, `EmailStr`, custom validators.

## 5. Settings and config

- `pydantic-settings` `BaseSettings`
- Loading from `.env`
- `extra="ignore"`
- Secrets kept out of git (`.gitignore` for `.env`)
- Config for DB URL, JWT secret/algo/expiry, and mail credentials

## 6. SQLAlchemy + Postgres

- Engine, `sessionmaker[Session]`, `DeclarativeBase`
- `get_db()` dependency with `yield` + `finally: session.close()`
- `Base.metadata.create_all(engine)`
- `Mapped` fields with `mapped_column`: `String`, `Boolean`, primary key, unique, nullable
- Foreign key `tasks.user_id → users.id` with `ondelete="CASCADE"`
- Session writes: `add`, `commit`, `refresh`, `delete`
- Session reads: `select().where()` with `scalars().first()` / `scalars().all()`, and `Session.get()` by primary key
- Partial updates with `setattr` from a dumped schema
- PostgreSQL via `psycopg[binary]`

Not used yet: SQLAlchemy `relationship()` / joins / eager loading.

## 7. Dependency injection

- `Depends(get_db)` for a request-scoped session
- `Depends(is_authenticated)` to inject the current user into task routes
- `Annotated[Session, Depends(...)]` / `Annotated[UserModel, Depends(...)]`

## 8. Auth and security

- Password hashing/verification with `pwdlib.PasswordHash`
- JWT encode/decode (`PyJWT`), including `exp`
- UTC + timedelta for token lifetime
- Reading `Authorization` from headers
- Duplicate username/email checks on register
- Login failure as 401
- Invalid/missing token as 401 (`InvalidTokenError`)

This is custom JWT auth, not FastAPI’s `OAuth2PasswordBearer` / Swagger “Authorize” flow.

## 9. Authorization (not just authentication)

- Tasks are owned by `user_id`
- List is filtered to the current user
- Get/update/delete check ownership and return 403 if it isn’t yours
- 404 when the task doesn’t exist

## 10. Background work and email

- FastAPI `BackgroundTasks`
- Fire-and-forget welcome email after register
- `fastapi-mail`: `ConnectionConfig`, `MessageSchema`, HTML body, Gmail SMTP over SSL

## 11. Python packaging / tooling

- `pyproject.toml` project metadata and dependencies
- Virtualenv
- Uvicorn
- `.gitignore` for secrets, venv, caches

`pytest` and `httpx` are listed as optional deps, and there is a `tests/` folder, but there are no tests written. Empty files that are planned and not used: `exception.py`, `logging.py`, `security.py`, `constants.py`, `dependencies.py`, `responses.py`, `api/v1/router.py`. Both `repository.py` files are in use.

---

```
fast/                                          8 files
├── .env
├── .env.example
├── .gitignore
├── LEARNING.md
├── alembic.ini
├── package.txt
├── progress.txt
└── pyproject.toml

├── .vscode/                                   1 file
│   └── settings.json

├── app/                                       2 files
│   ├── __init__.py
│   └── main.py
│
├── app/api/                                   2 files
│   ├── __init__.py
│   └── __init__ copy.py
│
├── app/api/v1/                                2 files
│   ├── __init__.py
│   └── router.py
│
├── app/common/                                5 files
│   ├── __init__.py
│   ├── constants.py
│   ├── dependencies.py
│   ├── responses.py
│   └── utils.py
│
├── app/core/                                  5 files
│   ├── __init__.py
│   ├── config.py
│   ├── exception.py
│   ├── logging.py
│   └── security.py
│
├── app/database/                              2 files
│   ├── __init__.py
│   └── connection.py
│
├── app/modules/                               1 file
│   └── __init__.py
│
├── app/modules/tasks/                         6 files
│   ├── __init__.py
│   ├── model.py
│   ├── repository.py
│   ├── router.py
│   ├── schema.py
│   └── service.py
│
└── app/modules/users/                         6 files
    ├── __init__.py
    ├── model.py
    ├── repository.py
    ├── router.py
    ├── schema.py
    └── service.py

migrations/                                    3 files
├── README
├── env.py
└── script.py.mako

migrations/versions/                           1 file
└── 91c11579653a_add_user_id_to_task_model.py

tests/                                         1 file
└── __init__.py

tests/integration/                             0 files
tests/unit/                                    0 files
```

## Code another LLM should follow

This is the code that is actually running. Do not invent a different layout. SQLAlchemy is 2.x: `DeclarativeBase`, `Mapped`, `mapped_column`, `select()`, `Session.scalars()`, `Session.get()`.

Request path:

```
HTTP → router → service → repository → Postgres
```

Task routes call `app.common.utils.is_authenticated`, which returns a `UserModel`. `GET /user/is_authenticated` calls `users/service.is_authenticated`, which returns JSON. Those are two different functions.

The password column is spelled `hased_password` in the model. Keep that spelling.

The real files also `print` the task body in `POST /tasks/create` and the token expiry during login. Those prints are not part of the response.

Empty files listed above have no code. Do not treat them as implemented.

### Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

`.env` keys (values stay in `.env`, not here):

```
DATABASE_CONNECTION=postgresql://USER:PASSWORD@localhost:5432/fastdb
SECRET_KEY=
TOKEN_ALGO=HS256
EXPIRY_TIME=30
EMAIL_SENDER=
MAIL_PASSWORD=
```

`@` in a Postgres password must be URL-encoded as `%40`. Alembic reads the same URL from settings. `%` is doubled to `%%` in `migrations/env.py` so configparser does not treat it as interpolation.

`alembic.ini` sets `script_location = migrations`. Models are imported in `migrations/env.py`, and `target_metadata = Base.metadata`.

Tables are also created on startup with `Base.metadata.create_all(engine)` in `main.py`. The one Alembic revision adds `user_tasks.user_id` as a foreign key to `users.id` with `ondelete='CASCADE'`.

### `pyproject.toml`

```toml
[project]
name = "fast"
version = "0.1.0"
description = "FastAPI backend with users, tasks, JWT auth, and email"
requires-python = ">=3.13"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "sqlalchemy",
    "alembic",
    "pydantic-settings",
    "psycopg[binary]",
    "PyJWT",
    "pwdlib[argon2]",
    "fastapi-mail",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "httpx",
]
```

### `app/core/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )

    DATABASE_CONNECTION: str
    SECRET_KEY: str
    TOKEN_ALGO: str
    EXPIRY_TIME: int
    EMAIL_SENDER: str
    MAIL_PASSWORD: str


settings = Settings()
```

### `app/database/connection.py`

```python
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine: Engine = create_engine(settings.DATABASE_CONNECTION)
localSession: sessionmaker[Session] = sessionmaker(bind=engine)


def get_db():

    session: Session = localSession()

    try:
        yield session
    finally:
        session.close()
```

### `app/main.py`

`TaskModel` is imported so the table is registered on `Base` before `create_all`. The user model is registered because `user_routes` imports it.

```python
from fastapi import FastAPI

from app.database.connection import Base, engine
from app.modules.tasks.model import TaskModel
from app.modules.tasks.router import task_routes
from app.modules.users.router import user_routes

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(task_routes)
app.include_router(user_routes)
```

Routes:

| Method | Path | Auth |
|---|---|---|
| POST | `/user/register` | no |
| POST | `/user/login` | no |
| GET | `/user/is_authenticated` | `Authorization` header |
| POST | `/tasks/create` | `Authorization` header |
| GET | `/tasks/all_tasks` | `Authorization` header |
| GET | `/tasks/get_task_by_id/{taskId}` | `Authorization` header |
| PUT | `/tasks/update_task_by_id/{taskId}` | `Authorization` header |
| DELETE | `/tasks/delete_task/{taskId}` | `Authorization` header |

### Users

`app/modules/users/model.py`

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hased_password: Mapped[str] = mapped_column(String, nullable=False)
    mobile_number: Mapped[str] = mapped_column(String, nullable=False, unique=True)
```

`app/modules/users/schema.py`

```python
import pydantic.config
from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    name: str
    username: str
    email: str
    password: str
    mobile_number: str


class UserPublicSchema(BaseModel):
    model_config: ConfigDict = ConfigDict(from_attributes=True)
    id: int
    name: str
    username: str
    email: str
    mobile_number: str


class UserResponseSchema(BaseModel):
    status: int
    message: str
    data: UserPublicSchema


class UserLoginSchema(BaseModel):
    email: str
    password: str


class UserPublicLoginSchema(BaseModel):
    model_config: ConfigDict = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    email: str
    mobile_number: str
    token: str


class UserResponseLoginSchema(BaseModel):
    status: int
    message: str
    data: UserPublicLoginSchema
```

`app/modules/users/repository.py`

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.model import UserModel


def get_user_by_username(db: Session, username: str) -> UserModel | None:
    return db.scalars(select(UserModel).where(UserModel.username == username)).first()


def get_user_by_email(db: Session, email: str) -> UserModel | None:
    return db.scalars(select(UserModel).where(UserModel.email == email)).first()


def get_user_by_id(db: Session, user_id: int) -> UserModel | None:
    return db.get(UserModel, user_id)


def create_user(db: Session, user: UserModel) -> UserModel:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

`app/modules/users/service.py`

Register checks username and email, hashes the password with `pwdlib`, inserts the user, then queues `sendEmail`. Login checks the password and returns a JWT with `id` and `exp`. `EXPIRY_TIME` is days. `is_authenticated` reads `Authorization`, decodes the JWT, and returns the public user plus the same token. Missing or bad tokens are 401.

```python
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import BackgroundTasks, HTTPException, Request, status
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.common.utils import sendEmail
from app.core.config import settings
from app.modules.users import repository
from app.modules.users.model import UserModel
from app.modules.users.schema import UserLoginSchema, UserPublicSchema, UserSchema

password_hash: PasswordHash = PasswordHash.recommended()


def hashPassword(password: str):
    return password_hash.hash(password)


def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
    return password_hash.verify(plainPassword, hashedPassword)


async def register(data: UserSchema, db: Session, bg_task: BackgroundTasks) -> Any:
    if repository.get_user_by_username(db, data.username):
        raise HTTPException(400, "Username already exists")

    if repository.get_user_by_email(db, data.email):
        raise HTTPException(400, "User email already exists")

    hashed_password = hashPassword(data.password)

    new_user = UserModel(
        name=data.name,
        email=data.email,
        username=data.username,
        hased_password=hashed_password,
        mobile_number=data.mobile_number,
    )

    new_user = repository.create_user(db, new_user)
    bg_task.add_task(sendEmail, [data.email], name=data.name)
    return {
        "status": status.HTTP_201_CREATED,
        "message": "User registered successfully",
        "data": new_user,
    }


def login(data: UserLoginSchema, db: Session):
    user: UserModel | None = repository.get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Entered email doesn't exists!"
        )

    if not verifyPassword(data.password, user.hased_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Entered password is incorrect!"
        )

    expiry_time: datetime = datetime.now(UTC) + timedelta(days=settings.EXPIRY_TIME)
    userToken: str = jwt.encode(
        {"id": user.id, "exp": expiry_time.timestamp()},
        settings.SECRET_KEY,
        settings.TOKEN_ALGO,
    )

    return {
        "status": status.HTTP_200_OK,
        "message": "User logged in successfully",
        "data": {
            **UserPublicSchema.model_validate(user).model_dump(),
            "token": userToken,
        },
    }


def is_authenticated(request: Request, db: Session):
    try:
        user_token: str = request.headers.get("Authorization", "").split(" ")[-1]

        decoded_token: Any | None = jwt.decode(
            user_token, settings.SECRET_KEY, settings.TOKEN_ALGO
        ).get("id")

        user: UserModel | None = repository.get_user_by_id(db, decoded_token)

        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are unauthorized!")

        return {
            "status": status.HTTP_200_OK,
            "message": "User details fetched successfully",
            "data": {
                **UserPublicSchema.model_validate(user).model_dump(),
                "token": user_token,
            },
        }

    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are unauthorized!")
```

`app/modules/users/router.py`

```python
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.users import service
from app.modules.users.schema import (
    UserLoginSchema,
    UserResponseLoginSchema,
    UserResponseSchema,
    UserSchema,
)

user_routes = APIRouter(prefix="/user")


@user_routes.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema
)
async def register(
    data: UserSchema, bg_task: BackgroundTasks, db: Annotated[Session, Depends(get_db)]
) -> Any:
    return await service.register(data, db, bg_task)


@user_routes.post(
    "/login", response_model=UserResponseLoginSchema, status_code=status.HTTP_200_OK
)
def login(data: UserLoginSchema, db: Annotated[Session, Depends(get_db)]):
    return service.login(data, db)


@user_routes.get(
    "/is_authenticated",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseLoginSchema,
)
def is_authenticated(request: Request, db: Annotated[Session, Depends(get_db)]):
    return service.is_authenticated(request, db)
```

### Tasks

`app/modules/tasks/model.py`

```python
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class TaskModel(Base):
    __tablename__ = "user_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str | None] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
```

`app/modules/tasks/schema.py`

```python
from pydantic import BaseModel


class TaskSchema(BaseModel):
    title: str
    description: str
    is_completed: bool = False
```

`app/modules/tasks/repository.py`

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.tasks.model import TaskModel


def create_task(db: Session, task: TaskModel) -> TaskModel:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks_by_user(db: Session, user_id: int) -> list[TaskModel]:
    return db.scalars(select(TaskModel).where(TaskModel.user_id == user_id)).all()


def get_task_by_id(db: Session, task_id: int) -> TaskModel | None:
    return db.get(TaskModel, task_id)


def save_task(db: Session, task: TaskModel) -> TaskModel:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: TaskModel) -> None:
    db.delete(task)
    db.commit()
```

`app/modules/tasks/service.py`

The service builds the row and checks ownership. Missing task is 404. A task owned by someone else is 403. Update copies every field from `TaskSchema` onto the model with `setattr`, then the repository commits.

```python
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.tasks import repository
from app.modules.tasks.model import TaskModel
from app.modules.tasks.schema import TaskSchema
from app.modules.users.model import UserModel


def create_task(task: TaskSchema, db: Session, user: UserModel):
    new_task = TaskModel(
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        user_id=user.id,
    )

    saved = repository.create_task(db, new_task)
    return {"message": "success", "data": saved}


def get_all_task(db: Session, user: UserModel):
    tasks = repository.get_tasks_by_user(db, user.id)
    return {"message": "success", "data": tasks}


def get_task_by_id(taskId: int, db: Session, user: UserModel):
    task = repository.get_task_by_id(db, taskId)

    if not task:
        raise HTTPException(404, detail="Task id not found")

    if user.id != task.user_id:
        raise HTTPException(403, detail="You are not allowed to get this task")

    return {"message": "success", "data": task}


def update_task_by_id(taskId: int, body: TaskSchema, db: Session, user: UserModel):
    task = repository.get_task_by_id(db, taskId)

    if not task:
        raise HTTPException(404, detail="Task id not found")

    if user.id != task.user_id:
        raise HTTPException(403, detail="You are not allowed to get this task")

    for key, value in body.model_dump().items():
        setattr(task, key, value)

    saved = repository.save_task(db, task)
    return {"message": "success", "data": saved}


def delete_task(taskId: int, db: Session, user: UserModel):
    task = repository.get_task_by_id(db, taskId)

    if not task:
        raise HTTPException(404, detail="Task id not found")

    if user.id != task.user_id:
        raise HTTPException(403, detail="You are not allowed to delete this task")

    repository.delete_task(db, task)
    return None
```

`app/modules/tasks/router.py`

```python
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.common.utils import is_authenticated
from app.database.connection import get_db
from app.modules.tasks import service
from app.modules.tasks.schema import TaskSchema
from app.modules.users.model import UserModel

task_routes = APIRouter(prefix="/tasks")


@task_routes.post("/create", status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskSchema,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserModel, Depends(is_authenticated)],
):
    return service.create_task(task=task, db=db, user=user)


@task_routes.get("/all_tasks", status_code=status.HTTP_200_OK)
def get_all_tasks(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserModel, Depends(is_authenticated)],
):
    return service.get_all_task(db=db, user=user)


@task_routes.get("/get_task_by_id/{taskId}")
def get_task_by_id(
    taskId: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserModel, Depends(is_authenticated)],
):
    return service.get_task_by_id(taskId, db, user)


@task_routes.put("/update_task_by_id/{taskId}")
def update_task_by_id(
    taskId: int,
    body: TaskSchema,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserModel, Depends(is_authenticated)],
):
    return service.update_task_by_id(taskId, body, db, user)


@task_routes.delete("/delete_task/{taskId}")
def delete_task(
    taskId: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserModel, Depends(is_authenticated)],
):
    return service.delete_task(taskId, db, user)
```

### `app/common/utils.py`

Used by task routes and by register. Mail is Gmail SMTP on port 465 with SSL. `_welcome_email_html(name)` returns the HTML body. `sendEmail` is async and is scheduled with `BackgroundTasks`.

```python
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db
from app.modules.users import repository
from app.modules.users.model import UserModel

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_SENDER,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_SENDER,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
)


def is_authenticated(request: Request, db: Annotated[Session, Depends(get_db)]):
    try:
        user_token: str = request.headers.get("Authorization", "").split(" ")[-1]

        decoded_token: Any | None = jwt.decode(
            user_token, settings.SECRET_KEY, settings.TOKEN_ALGO
        ).get("id")

        user: UserModel | None = repository.get_user_by_id(db, decoded_token)

        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are unauthorized!")

        return user

    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are unauthorized!")


async def sendEmail(emails: list[str], name: str | None = None) -> Any:
    message = MessageSchema(
        subject="Welcome — your account is ready",
        recipients=emails,
        body=_welcome_email_html(name),
        subtype=MessageType.html,
    )
    await FastMail(conf).send_message(message)
    return {"message": "email has been sent"}
```

### Migration `91c11579653a_add_user_id_to_task_model.py`

```python
def upgrade() -> None:
    op.add_column("user_tasks", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "user_tasks", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_constraint(None, "user_tasks", type_="foreignkey")
    op.drop_column("user_tasks", "user_id")
```
