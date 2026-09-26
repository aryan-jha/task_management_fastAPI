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
