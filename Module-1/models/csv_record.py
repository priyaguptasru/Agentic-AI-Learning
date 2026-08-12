from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class CSVRecord(Base):

    __tablename__ = "csv_records"

    record_id = Column(
        Integer,
        primary_key=True
    )

    file_id = Column(
        Integer,
        ForeignKey(
            "csv_files.file_id"
        ),
        index=True
    )

    record_data = Column(
        JSONB,
        nullable=False
    )