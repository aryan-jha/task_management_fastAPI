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
