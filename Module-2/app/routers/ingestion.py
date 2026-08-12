from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import BackgroundTasks

from app.services.ingestion_service import (
    save_pdf_file,
    save_csv_file
)

router = APIRouter(
    prefix="/ingest",
    tags=["Ingestion"]
)


# ----------------------------------
# PDF INGESTION
# ----------------------------------

@router.post("/pdf")
async def ingest_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    return await save_pdf_file(
    file,
    background_tasks
)


# ----------------------------------
# CSV INGESTION
# ----------------------------------

@router.post("/csv")
async def ingest_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    return await save_csv_file(
    file,
    background_tasks
)