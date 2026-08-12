from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from app.core.database import Base


class Section(Base):

    __tablename__ = "sections"

    section_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    page_id = Column(
        Integer,
        ForeignKey("pages.page_id"),
        nullable=False
    )

    header = Column(
        String,
        nullable=False
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