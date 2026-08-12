from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


# ---------------------------------------------------
# DATABASE URL
# ---------------------------------------------------

DATABASE_URL = (
    "postgresql://postgres:123456789@localhost:5432/module1_db"
)


# ---------------------------------------------------
# CREATE ENGINE
# ---------------------------------------------------

engine = create_engine(
    DATABASE_URL
)


# ---------------------------------------------------
# SESSION FACTORY
# ---------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ---------------------------------------------------
# BASE CLASS
# ---------------------------------------------------

Base = declarative_base()


# ---------------------------------------------------
# DATABASE DEPENDENCY
# ---------------------------------------------------

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()