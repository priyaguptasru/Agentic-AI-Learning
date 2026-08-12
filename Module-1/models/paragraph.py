from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from .database import Base


class Paragraph(Base):

    __tablename__ = "paragraphs"

    paragraph_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    section_id = Column(
        Integer,
        ForeignKey(
            "sections.section_id"
        ),
        index=True
    )

    text = Column(
        Text
    )

    section = relationship(
        "Section",
        back_populates="paragraphs"
    )