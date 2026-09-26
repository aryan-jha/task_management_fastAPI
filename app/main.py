from app.modules.tasks.router import task_routes
from fastapi import FastAPI
from app.database.connection import Base, engine
from app.modules.tasks.model import TaskModel
Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(task_routes)