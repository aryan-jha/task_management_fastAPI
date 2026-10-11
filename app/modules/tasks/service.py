from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, relationship

from app.modules.tasks import repository
from app.modules.tasks.model import TaskModel
from app.modules.tasks.schema import TaskSchema
from app.modules.users.model import UserModel
from app.modules.users.router import user_routes


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


def get_all_completed_task(db: Session, user: UserModel):

    task: list[TaskModel] = repository.get_all_completed_task(db, user)

    return {"message": "success", "data": task}


# 1
def get_all_latest_tasks(db: Session, user: UserModel):

    result: list[TaskModel] = db.scalars(
        select(TaskModel)
        .where(TaskModel.user_id == user.id)
        .order_by(TaskModel.id.desc())
    ).all()

    return result


# 2
def get_all_task_newest_first(db: Session, user: UserModel):

    result: list[TaskModel] = db.scalars(
        select(TaskModel).where(TaskModel.user_id == user.id).order_by(TaskModel.id)
    ).all()

    return result


# 3, 4, 5 and 7 combined
def get_tasks_paginated(db: Session, user: UserModel, page: int = 1, limit: int = 10):

    calculatedOffset: int = (page - 1) * limit

    result: list[TaskModel] = db.scalars(
        select(TaskModel)
        .where(TaskModel.user_id == user.id)
        .order_by(TaskModel.id)
        .offset(offset=calculatedOffset)
        .limit(limit)
    ).all()

    return result


# 6
def particular_user_data(db: Session, user: UserModel):

    result: list[TaskModel] = db.scalars(
        select(TaskModel)
        .where(TaskModel.user_id == 2, TaskModel.is_completed == True)
        .order_by(TaskModel.id)
        .limit(10)
    ).all()

    return result
