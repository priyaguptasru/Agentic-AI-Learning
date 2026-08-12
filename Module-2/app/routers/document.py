from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.document_service import (
    get_all_documents,
    get_document_by_id,
    get_document_content
)
from app.schemas.document_schema import DocumentResponse

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# ---------------------------------------------------
# GET ALL DOCUMENTS
# ---------------------------------------------------

@router.get("/")
def fetch_documents(
    db: Session = Depends(get_db)
):

    return get_all_documents(db)


# ---------------------------------------------------
# GET DOCUMENT BY ID
# ---------------------------------------------------

@router.get("/{document_id}")
def fetch_document_by_id(

    document_id: int,

    db: Session = Depends(get_db)

):

    print("=" * 60)
    print("Router received document_id:", document_id)

    document = get_document_by_id(
        document_id,
        db
    )

    print("Router received document:", document)

    if document is None:

        print("Returning 404")

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    print("Returning document successfully")
    print("=" * 60)

    return document

# ---------------------------------------------------
# GET DOCUMENT CONTENT
# ---------------------------------------------------

@router.get(
    "/{document_id}/content",
    response_model=DocumentResponse
)
def fetch_document_content(

    document_id: int,

    db: Session = Depends(get_db)

):

    document = get_document_content(
        document_id,
        db
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return document