import os

from fastapi import UploadFile
from fastapi import HTTPException


# ----------------------------------
# ALLOWED FILE TYPES
# ----------------------------------

ALLOWED_PDF = ".pdf"

ALLOWED_CSV = ".csv"


# ----------------------------------
# MAX FILE SIZE
# ----------------------------------

MAX_FILE_SIZE = 10 * 1024 * 1024


# ----------------------------------
# VALIDATE EXTENSION
# ----------------------------------

def validate_extension(
    file: UploadFile,
    extension: str
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )

    if not file.filename.lower().endswith(extension):

        raise HTTPException(
            status_code=400,
            detail=f"Only {extension} files are allowed."
        )
    

    # ----------------------------------
# DUPLICATE FILE CHECK
# ----------------------------------

def validate_duplicate(
    file_name: str,
    folder: str
):

    file_path = os.path.join(
        folder,
        file_name
    )

    if os.path.exists(file_path):

        raise HTTPException(
            status_code=409,
            detail="File already exists."
        )
    

    # ----------------------------------
# FILE SIZE VALIDATION
# ----------------------------------

async def validate_size(
    file: UploadFile
):

    content = await file.read()

    size = len(content)

    await file.seek(0)

    if size == 0:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if size > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail="File size exceeds 10 MB."
        )