import os
import sys

from app.utils.file_transfer import (
    copy_file,
    clear_folder
)

# ----------------------------------
# ADD MODULE-1 TO PYTHON PATH
# ----------------------------------

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODULE2_DIR = os.path.dirname(
    os.path.dirname(CURRENT_DIR)
)

PROJECT_ROOT = os.path.dirname(
    MODULE2_DIR
)

MODULE1_DIR = os.path.join(
    PROJECT_ROOT,
    "Module-1"
)

# ----------------------------------
# MODULE-1 INPUT FOLDERS
# ----------------------------------

MODULE1_PDF_FOLDER = os.path.join(
    MODULE1_DIR,
    "data",
    "pdfs"
)

MODULE1_CSV_FOLDER = os.path.join(
    MODULE1_DIR,
    "data",
    "csvs"
)

# ----------------------------------
# MODULE-1 OUTPUT FOLDERS
# ----------------------------------

MODULE1_TEXT_FOLDER = os.path.join(
    MODULE1_DIR,
    "output",
    "text"
)

MODULE1_JSON_FOLDER = os.path.join(
    MODULE1_DIR,
    "output",
    "json"
)

MODULE1_NORMALIZED_JSON_FOLDER = os.path.join(
    MODULE1_DIR,
    "output",
    "normalized_json"
)

MODULE1_CLEANED_CSV_FOLDER = os.path.join(
    MODULE1_DIR,
    "output",
    "cleaned_csv"
)

# ----------------------------------
# ADD MODULE-1 TO PYTHON PATH
# ----------------------------------

if MODULE1_DIR not in sys.path:

    sys.path.append(
        MODULE1_DIR
    )

from scripts.check_document_exists import document_exists

from scripts.clear_database import clear_database

from scripts.extract_all_pdfs import (
    extract_all_pdfs
)

from scripts.detect_document_structure import (
    detect_document_structure
)

from scripts.normalize_json import (
    normalize_json
)

from scripts.load_json_to_db import (
    load_json_to_db
)

from scripts.clean_csv_data import (
    clean_csv_data
)

from scripts.load_csv_to_db import (
    load_csv_to_db
)

# ----------------------------------
# PDF PIPELINE
# ----------------------------------

def process_pdf_pipeline(
    file_path: str
):

    print(
        f"\nStarted Processing PDF: {file_path}"
    )

    try:

        # ----------------------------------
        # CLEAR OLD PDF INPUT/OUTPUT FILES
        # ----------------------------------

        clear_folder(
            MODULE1_PDF_FOLDER
        )

        clear_folder(
            MODULE1_TEXT_FOLDER
        )

        clear_folder(
            MODULE1_JSON_FOLDER
        )

        clear_folder(
            MODULE1_NORMALIZED_JSON_FOLDER
        )

        # ----------------------------------
        # COPY PDF TO MODULE-1
        # ----------------------------------

        copy_file(
            file_path,
            MODULE1_PDF_FOLDER
        )

        print(
            "PDF copied to Module-1 successfully."
        )

        # ----------------------------------
        # EXECUTE PDF PIPELINE
        # ----------------------------------

        extract_all_pdfs()

        detect_document_structure()

        normalize_json()
        
        pdf_name = os.path.basename(file_path)

        if document_exists(pdf_name):

            print(f"{pdf_name} already exists in database.")

            print("Skipping database reload.")

            return
        
        clear_database()

        # ----------------------------------
        # LOAD INTO DATABASE
        # Duplicate detection is handled
        # inside load_json_to_db().
        # ----------------------------------

        load_json_to_db()

        print(
            "PDF Pipeline Completed Successfully!"
        )

    except Exception as e:

        print(
            f"PDF Pipeline Failed: {e}"
        )


# ----------------------------------
# CSV PIPELINE
# ----------------------------------

def process_csv_pipeline(
    file_path: str
):

    print(
        f"\nStarted Processing CSV: {file_path}"
    )

    try:

        # ----------------------------------
        # KEEP ALL CSV FILES
        # ----------------------------------

        # clear_folder(
        #     MODULE1_CSV_FOLDER
        # )

        # ----------------------------------
        # KEEP ALL CLEANED CSV FILES
        # ----------------------------------

        # clear_folder(
        #     MODULE1_CLEANED_CSV_FOLDER
        # )

        # ----------------------------------
        # COPY CSV
        # ----------------------------------

        copy_file(
            file_path,
            MODULE1_CSV_FOLDER
        )

        print(
            "CSV copied to Module-1 successfully."
        )

        # ----------------------------------
        # EXECUTE CSV PIPELINE
        # ----------------------------------

        clean_csv_data()

        load_csv_to_db()

        print(
            "CSV Pipeline Completed Successfully!"
        )

    except Exception as e:

        print(
            f"CSV Pipeline Failed: {e}"
        )