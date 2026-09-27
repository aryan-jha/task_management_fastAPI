from fastapi import FastAPI

from app.database.connection import Base, engine
from app.modules.tasks.model import TaskModel
from app.modules.tasks.router import task_routes
from app.modules.users.router import user_routes

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(task_routes)
app.include_router(user_routes)
