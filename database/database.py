import os

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from constants import APP_DATA_FOLDER, NO_CATEGORY_TEXT
from database.models import Base, Category
from tools import create_folders

create_folders()
__all__ = ["startup", "session"]

DATABASE_URL = f"sqlite:///{os.path.join(APP_DATA_FOLDER, 'data.db')}"

engine = create_engine(
    DATABASE_URL, poolclass=StaticPool, connect_args={"check_same_thread": False}
)
metadata = MetaData()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


def startup() -> None:
    """
    Create and initialize the necessary database tables.
    This function creates and initializes the necessary database tables for the application.
    It uses the `metadata` object to create all the tables defined in the SQLAlchemy models.
    The `engine` object is used to connect to the database and execute the necessary SQL statements.

    Returns:
        None
    """
    Base.metadata.create_all(engine)
    no_category = session.query(Category).filter_by(title=NO_CATEGORY_TEXT).first()

    if not no_category:
        new_category = Category(title=NO_CATEGORY_TEXT)
        session.add(new_category)
        session.commit()

    session.close()
