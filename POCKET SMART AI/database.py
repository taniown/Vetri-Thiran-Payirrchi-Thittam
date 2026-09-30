from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


settings = get_settings()

database_url = settings.database_url


# Create the database folder if using SQLite
if database_url.startswith("sqlite:///"):
    db_path = database_url.replace(
        "sqlite:///",
        "",
        1,
    )

    Path(db_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )


# SQLite configuration
connect_args = {}

if database_url.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }


# Database engine
engine = create_engine(
    database_url,
    connect_args=connect_args,
)


# Database session
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Database dependency
def get_db():
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()