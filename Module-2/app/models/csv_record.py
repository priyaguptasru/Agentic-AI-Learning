from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import relationship

from app.core.database import Base


class CSVRecord(Base):

    __tablename__ = "csv_records"

    record_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_id = Column(
        Integer,
        ForeignKey("csv_files.file_id"),
        nullable=False
    )

    record_data = Column(
        JSONB,
        nullable=False
    )

    csv_file = relationship(
        "CSVFile",
        back_populates="records"
    )