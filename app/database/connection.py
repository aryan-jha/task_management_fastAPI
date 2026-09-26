from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


Base = declarative_base()
engine = create_engine(url=settings.DATABASE_CONNECTION)
localSession = sessionmaker(bind=engine)

def get_db():
    
    session = localSession()
    
    try:
        yield session
    finally:
        session.close()