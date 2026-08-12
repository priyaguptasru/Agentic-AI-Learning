from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import relationship

from app.core.database import Base


class CSVFile(Base):

    __tablename__ = "csv_files"

    file_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_name = Column(
        String,
        nullable=False
    )

    total_rows = Column(
        Integer,
        nullable=False
    )

    records = relationship(
        "CSVRecord",
        back_populates="csv_file",
        cascade="all, delete-orphan"
    )