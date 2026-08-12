from models.session import SessionLocal
from models.document import Document


def document_exists(document_name: str):

    db = SessionLocal()

    try:

        document = (

            db.query(Document)

            .filter(
                Document.document_name == document_name
            )

            .first()

        )

        return document is not None

    finally:

        db.close()