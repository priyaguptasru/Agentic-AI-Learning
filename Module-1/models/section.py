from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from .database import Base


class Section(Base):

    __tablename__ = "sections"

    section_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    page_id = Column(
        Integer,
        ForeignKey(
            "pages.page_id"
        ),
        index=True
    )

    header = Column(
        String,
        index=True
    )

    page = relationship(
        "Page",
        back_populates="sections"
    )

    paragraphs = relationship(
        "Paragraph",
        back_populates="section",
        cascade="all, delete-orphan"
    )