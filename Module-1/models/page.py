from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from .database import Base


class Page(Base):

    __tablename__ = "pages"

    page_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    document_id = Column(
        Integer,
        ForeignKey(
            "documents.document_id"
        ),
        index=True
    )

    page_number = Column(
        Integer,
        nullable=False
    )

    document = relationship(
        "Document",
        back_populates="pages"
    )

    sections = relationship(
        "Section",
        back_populates="page",
        cascade="all, delete-orphan"
    )