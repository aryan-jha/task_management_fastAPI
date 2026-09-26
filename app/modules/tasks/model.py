from sqlalchemy import Column, Integer, String, Boolean
from app.database.connection import Base

class TaskModel(Base):
    
    __tablename__ = 'user_tasks'

    id:Column[int] = Column(Integer, primary_key=True)
    title:Column[str] = Column(String)
    description:Column[str] = Column(String)
    is_completed:Column[bool] = Column(Boolean, default=False)