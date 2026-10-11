from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine: Engine = create_engine(settings.DATABASE_CONNECTION)
localSession: sessionmaker[Session] = sessionmaker(bind=engine)


def get_db():

    session: Session = localSession()

    try:
        yield session
    finally:
        session.close()
