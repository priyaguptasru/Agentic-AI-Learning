from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.csv_schema import (
    CSVFileResponse,
    CSVFileContentResponse
)

from app.services.csv_service import (
    get_all_csv_files,
    get_csv_file_by_id,
    get_csv_content
)

router = APIRouter(
    prefix="/csv",
    tags=["CSV"]
)


# ----------------------------------
# GET ALL CSV FILES
# ----------------------------------

@router.get(
    "/files",
    response_model=list[CSVFileResponse]
)
def fetch_csv_files(

    db: Session = Depends(get_db)

):

    return get_all_csv_files(db)


# ----------------------------------
# GET CSV FILE
# ----------------------------------

@router.get(
    "/files/{file_id}",
    response_model=CSVFileResponse
)
def fetch_csv_file(

    file_id: int,

    db: Session = Depends(get_db)

):

    csv_file = get_csv_file_by_id(
        file_id,
        db
    )

    if csv_file is None:

        raise HTTPException(
            status_code=404,
            detail="CSV file not found."
        )

    return csv_file


# ----------------------------------
# GET CSV CONTENT
# ----------------------------------

@router.get(
    "/files/{file_id}/records",
    response_model=CSVFileContentResponse
)
def fetch_csv_records(

    file_id: int,

    db: Session = Depends(get_db)

):

    csv_file = get_csv_content(
        file_id,
        db
    )

    if csv_file is None:

        raise HTTPException(
            status_code=404,
            detail="CSV file not found."
        )

    return csv_file