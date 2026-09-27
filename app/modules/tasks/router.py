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

    print(task.model_dump())
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
