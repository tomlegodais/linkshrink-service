from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from .config import Config

engine = create_engine(Config.POSTGRES_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()
