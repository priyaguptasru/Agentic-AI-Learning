from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import relationship

from .database import Base


class Document(Base):

    __tablename__ = "documents"

    document_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    document_name = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )

    pages = relationship(
        "Page",
        back_populates="document",
        cascade="all, delete-orphan"
    )