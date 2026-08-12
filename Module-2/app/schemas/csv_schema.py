from pydantic import BaseModel
from pydantic import ConfigDict


# ----------------------------------
# CSV FILE RESPONSE
# ----------------------------------

class CSVFileResponse(BaseModel):

    file_id: int

    file_name: str

    total_rows: int

    model_config = ConfigDict(
        from_attributes=True
    )


# ----------------------------------
# CSV RECORD RESPONSE
# ----------------------------------

class CSVRecordResponse(BaseModel):

    record_id: int

    record_data: dict

    model_config = ConfigDict(
        from_attributes=True
    )


# ----------------------------------
# COMPLETE CSV FILE
# ----------------------------------

class CSVFileContentResponse(BaseModel):

    file_id: int

    file_name: str

    total_rows: int

    records: list[CSVRecordResponse]

    model_config = ConfigDict(
        from_attributes=True
    )