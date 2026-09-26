from sqlalchemy.orm import Session

from app.modules.tasks.model import TaskModel
from app.modules.tasks.schema import TaskSchema


def create_task(task: TaskSchema, db: Session):
    new_task = TaskModel(
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"message": "success", "data": new_task}
