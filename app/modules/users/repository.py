from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.model import UserModel


def get_user_by_username(db: Session, username: str) -> UserModel | None:
    return db.scalars(select(UserModel).where(UserModel.username == username)).first()


def get_user_by_email(db: Session, email: str) -> UserModel | None:
    return db.scalars(select(UserModel).where(UserModel.email == email)).first()


def get_user_by_id(db: Session, user_id: int) -> UserModel | None:
    return db.get(UserModel, user_id)


def create_user(db: Session, user: UserModel) -> UserModel:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
