from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.csv_file import CSVFile
from app.models.csv_record import CSVRecord


# ----------------------------------
# GET ALL CSV FILES
# ----------------------------------

def get_all_csv_files(
    db: Session
):

    return (
        db.query(CSVFile)
        .all()
    )


# ----------------------------------
# GET CSV FILE BY ID
# ----------------------------------

def get_csv_file_by_id(
    file_id: int,
    db: Session
):

    return (

        db.query(CSVFile)

        .filter(
            CSVFile.file_id == file_id
        )

        .first()

    )


# ----------------------------------
# GET CSV CONTENT
# ----------------------------------

def get_csv_content(
    file_id: int,
    db: Session
):

    return (

        db.query(CSVFile)

        .options(
            joinedload(CSVFile.records)
        )

        .filter(
            CSVFile.file_id == file_id
        )

        .first()

    )