from fastapi import HTTPException
from sqlalchemy.orm import Session

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

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"message": "success", "data": new_task}


def get_all_task(db: Session, user: UserModel):

    tasks: list[TaskModel] = (
        db.query(TaskModel).filter(user.id == TaskModel.user_id).all()
    )

    return {"message": "success", "data": tasks}


def get_task_by_id(taskId: int, db: Session, user: UserModel):

    task: TaskModel = db.query(TaskModel).get(taskId)

    if not user.id == task.user_id:
        raise HTTPException(403, detail="You are not allowed to get this task")

    if not task:
        raise HTTPException(404, detail="Task id not found")

    return {"message": "success", "data": task}


def update_task_by_id(taskId: int, body: TaskSchema, db: Session, user: UserModel):

    task: TaskModel = db.query(TaskModel).get(taskId)

    if user.id != task.user_id:
        raise HTTPException(403, detail="You are not allowed to get this task")

    if not task:
        raise HTTPException(404, detail="Task id not found")

    body = body.model_dump()
    for key, value in body.items():
        setattr(task, key, value)

    db.add(task)
    db.commit()
    db.refresh(task)

    return {"message": "success", "data": task}


def delete_task(taskId: int, db: Session, user: UserModel):

    task: TaskModel = db.query(TaskModel).get(taskId)

    if not user.id == task.user_id:
        raise HTTPException(403, detail="You are not allowed to delete this task")

    if not task:
        raise HTTPException(404, detail="Task id not found")

    db.delete(task)
    db.commit()

    return None
