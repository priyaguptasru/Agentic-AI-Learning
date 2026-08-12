import os
import shutil

from fastapi import HTTPException, UploadFile
from fastapi import BackgroundTasks

from app.utils.file_validator import (
    validate_extension,
    validate_size,
    ALLOWED_PDF,
    ALLOWED_CSV
)

from app.utils.file_transfer import (
    clear_folder
)

from app.services.pipeline_service import (
    process_pdf_pipeline,
    process_csv_pipeline
)


# ---------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


# ---------------------------------------------------
# UPLOAD FOLDERS
# ---------------------------------------------------

PDF_UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads",
    "pdfs"
)

CSV_UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads",
    "csvs"
)

os.makedirs(
    PDF_UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    CSV_UPLOAD_FOLDER,
    exist_ok=True
)


# ---------------------------------------------------
# SAVE PDF
# ---------------------------------------------------

async def save_pdf_file(
    file: UploadFile,
    background_tasks: BackgroundTasks
):

    validate_extension(
        file,
        ALLOWED_PDF
    )

    await validate_size(file)

    # ----------------------------------
    # CLEAR OLD UPLOADS
    # ----------------------------------

    clear_folder(
        PDF_UPLOAD_FOLDER
    )

    file_path = os.path.join(
        PDF_UPLOAD_FOLDER,
        file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    background_tasks.add_task(
        process_pdf_pipeline,
        file_path
    )

    return {
        "status": "accepted",
        "message": "PDF uploaded successfully. Processing started.",
        "filename": file.filename
    }


# ---------------------------------------------------
# SAVE CSV
# ---------------------------------------------------

async def save_csv_file(
    file: UploadFile,
    background_tasks: BackgroundTasks
):

    validate_extension(
        file,
        ALLOWED_CSV
    )

    await validate_size(file)

    # ----------------------------------
    # CLEAR OLD UPLOADS
    # ----------------------------------

    clear_folder(
        CSV_UPLOAD_FOLDER
    )

    file_path = os.path.join(
        CSV_UPLOAD_FOLDER,
        file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    background_tasks.add_task(
        process_csv_pipeline,
        file_path
    )

    return {
        "status": "accepted",
        "message": "CSV uploaded successfully. Processing started.",
        "filename": file.filename
    }