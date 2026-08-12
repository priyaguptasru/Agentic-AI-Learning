from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# PostgreSQL connection string
DATABASE_URL = (
    "postgresql://postgres:123456789@localhost:5432/module1_db"
)

# Engine handles DB connection
engine = create_engine(DATABASE_URL)

# Base class for all ORM models
Base = declarative_base()