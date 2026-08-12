from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import relationship

from app.core.database import Base


class Document(Base):

    __tablename__ = "documents"

    document_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    document_name = Column(
        String,
        nullable=False
    )

    pages = relationship(
        "Page",
        back_populates="document",
        cascade="all, delete-orphan"
    )