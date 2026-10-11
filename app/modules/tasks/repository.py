from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select

from app.modules.tasks.model import TaskModel
from app.modules.users.model import UserModel


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


def get_all_completed_task(db: Session, user: UserModel) -> list[TaskModel]:

    result: list[TaskModel] = list(
        db.scalars(
            select(TaskModel).where(
                TaskModel.user_id == user.id, TaskModel.is_completed == True
            )
        )
    )

    return result


def get_tasks(
    db: Session,
    user_id: int,
    completed: bool | None = None,
    search: str | None = None,
) -> list[TaskModel]:

    stmt: Select[TaskModel] = select(TaskModel).where(
        # user filter
        TaskModel.user_id == user_id
    )

    # add completed filter only if provided
    if completed is not None:
        stmt.where(TaskModel.is_completed == True)

    # add search filter only if provided
    if search is not None:
        stmt.where(TaskModel.title.ilike(f"{search}"))

    return list(db.scalars(stmt).all())
