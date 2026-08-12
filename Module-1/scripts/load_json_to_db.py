import os
import json

from scripts.logger import log_error

from models.session import SessionLocal

from models.document import Document
from models.page import Page
from models.section import Section
from models.paragraph import Paragraph


# ----------------------------------
# LOAD JSON TO DATABASE
# ----------------------------------

def load_json_to_db():

    # ----------------------------------
    # FIND NORMALIZED JSON FOLDER
    # ----------------------------------

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    json_folder = os.path.join(
        base_dir,
        "output",
        "normalized_json"
    )

    # ----------------------------------
    # CREATE DATABASE SESSION
    # ----------------------------------

    db = SessionLocal()

    try:

        # ----------------------------------
        # PROCESS EACH JSON FILE
        # ----------------------------------

        for file_name in os.listdir(json_folder):

            if not file_name.endswith(".json"):
                continue

            print(f"\nProcessing: {file_name}")

            file_path = os.path.join(
                json_folder,
                file_name
            )

            # ----------------------------------
            # READ JSON
            # ----------------------------------

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

            except Exception as e:

                log_error(
                    f"JSON Read Failed | "
                    f"{file_name} | {e}"
                )

                print(f"Skipped: {file_name}")

                continue

            # ----------------------------------
            # CHECK DUPLICATE DOCUMENT
            # ----------------------------------

            existing_document = (

                db.query(Document)

                .filter(

                    Document.document_name == data["document_name"]

                )

                .first()

            )

            if existing_document:

                print(
                    f"Already Loaded: {data['document_name']}"
                )

                continue

            # ----------------------------------
            # INSERT DOCUMENT
            # ----------------------------------

            try:

                document = Document(
                    document_name=data["document_name"]
                )

                db.add(document)

                db.flush()

                # ------------------------------
                # INSERT PAGES
                # ------------------------------

                for page_data in data["pages"]:

                    page = Page(
                        document_id=document.document_id,
                        page_number=page_data["page_number"]
                    )

                    db.add(page)

                    db.flush()

                    # --------------------------
                    # INSERT SECTIONS
                    # --------------------------

                    for section_data in page_data["sections"]:

                        section = Section(
                            page_id=page.page_id,
                            header=section_data["header"]
                        )

                        db.add(section)

                        db.flush()

                        # ----------------------
                        # INSERT PARAGRAPHS
                        # ----------------------

                        for paragraph_data in section_data["paragraphs"]:

                            paragraph_text = (
                                str(
                                    paragraph_data.get(
                                        "text",
                                        ""
                                    )
                                )
                                .replace("\x00", "")
                                .strip()
                            )

                            paragraph = Paragraph(
                                section_id=section.section_id,
                                text=paragraph_text
                            )
                            
                            db.add(paragraph)

                db.commit()

                print(
                    f"Loaded: {file_name}"
                )

            except Exception as e:

                db.rollback()

                log_error(
                    f"Database Load Failed | "
                    f"{file_name} | {e}"
                )

                print(
                    f"Skipped: {file_name}"
                )

                continue

    finally:

        # ----------------------------------
        # CLOSE DATABASE SESSION
        # ----------------------------------

        db.close()

    print(
        "\nAll JSON files loaded successfully!"
    )


# ----------------------------------
# MAIN
# ----------------------------------

if __name__ == "__main__":

    load_json_to_db()