from pydantic import BaseModel
from pydantic import ConfigDict


# ---------------------------------------------------
# PARAGRAPH RESPONSE
# ---------------------------------------------------

class ParagraphResponse(BaseModel):

    paragraph_id: int

    text: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ---------------------------------------------------
# SECTION RESPONSE
# ---------------------------------------------------

class SectionResponse(BaseModel):

    section_id: int

    header: str

    paragraphs: list[ParagraphResponse]

    model_config = ConfigDict(
        from_attributes=True
    )


# ---------------------------------------------------
# PAGE RESPONSE
# ---------------------------------------------------

class PageResponse(BaseModel):

    page_id: int

    page_number: int

    sections: list[SectionResponse]

    model_config = ConfigDict(
        from_attributes=True
    )


# ---------------------------------------------------
# DOCUMENT RESPONSE
# ---------------------------------------------------

class DocumentResponse(BaseModel):

    document_id: int

    document_name: str

    pages: list[PageResponse]

    model_config = ConfigDict(
        from_attributes=True
    )