from sqlalchemy import Column, DateTime, Integer, String

from app.database.connection import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Column[int] = Column(Integer, primary_key=True)
    name: Column[str] = Column(String)
    username: Column[str] = Column(String, nullable=False)
    email: Column[str] = Column(String, nullable=False, unique=True)
    hased_password: Column[str] = Column(String, nullable=False)
    mobile_number: Column[str] = Column(String, nullable=False)
