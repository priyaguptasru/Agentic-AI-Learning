from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.document import Document
from app.models.page import Page
from app.models.section import Section
from app.models.paragraph import Paragraph


# ---------------------------------------------------
# GET ALL DOCUMENTS
# ---------------------------------------------------

def get_all_documents(
    db: Session
):

    documents = (
        db.query(Document)
        .all()
    )

    return documents


# ---------------------------------------------------
# GET DOCUMENT BY ID
# ---------------------------------------------------

def get_document_by_id(
    document_id: int,
    db: Session
):

    print(f"Searching document id = {document_id}")

    documents = db.query(Document).all()

    print("Documents in DB:")

    for doc in documents:
        print(doc.document_id, doc.document_name)

    document = (
        db.query(Document)
        .filter(Document.document_id == document_id)
        .first()
    )

    print("Query Result:", document)

    return document

# ---------------------------------------------------
# GET DOCUMENT CONTENT
# ---------------------------------------------------

def get_document_content(
    document_id: int,
    db: Session
):

    document = (

        db.query(Document)

        .options(

            joinedload(Document.pages)

            .joinedload(Page.sections)

            .joinedload(Section.paragraphs)

        )

        .filter(
            Document.document_id == document_id
        )

        .first()

    )

    return document