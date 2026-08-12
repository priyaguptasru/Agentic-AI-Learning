from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from datetime import datetime

from .database import Base


class CSVFile(Base):

    __tablename__ = "csv_files"

    file_id = Column(
        Integer,
        primary_key=True
    )

    file_name = Column(
        String,
        nullable=False,
        index=True
    )

    total_rows = Column(
        Integer
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )