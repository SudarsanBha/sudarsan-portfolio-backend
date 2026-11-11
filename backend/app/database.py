from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

# Local developement database.
# The SQLite database file will live in the backend folder
# DATABASE_URL = "sqlite:///./portofolio.db"
DATABASE_URL = settings.database_url

# SQLite needs this setting when used with fastapi.
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else{}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy database models."""
    pass


def get_db():
    """Provide a database session to a request and close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()