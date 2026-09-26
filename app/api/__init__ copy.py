from typing import Any

from sqlalchemy.orm import Session

from app.modules.tasks.model import TaskModel
from app.modules.tasks.schema import TaskSchema


def create_task(task: TaskSchema, db: Session):
    print("Inside service file ", task.model_dump())
    data: dict[str, Any] = task.model_dump()

    new_task: TaskModel = TaskModel(
        title=data["title"],
        description=data["description"],
        is_completed=data["is_completed"],
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"message": "success", "data": new_task}
