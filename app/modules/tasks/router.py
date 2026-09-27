from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.tasks import service
from app.modules.tasks.schema import TaskSchema

task_routes = APIRouter(prefix="/tasks")


@task_routes.post("/create", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskSchema, db: Annotated[Session, Depends(get_db)]):

    print(task.model_dump())
    return service.create_task(task=task, db=db)


@task_routes.get("/all_tasks", status_code=status.HTTP_200_OK)
def get_all_tasks(db: Annotated[Session, Depends(get_db)]):

    return service.get_all_task(db=db)


@task_routes.get("/get_task_by_id/{taskId}")
def get_task_by_id(taskId: int, db: Annotated[Session, Depends(get_db)]):

    return service.get_task_by_id(taskId, db)


@task_routes.get("/update_task_by_id/{taskId}")
def update_task_by_id(
    taskId: int, body: TaskSchema, db: Annotated[Session, Depends(get_db)]
):

    return service.update_task_by_id(taskId, body, db)


@task_routes.delete("/delete_task/{taskId}")
def delete_task(taskId: int, db: Annotated[Session, Depends(get_db)]):

    return service.delete_task(taskId, db)
