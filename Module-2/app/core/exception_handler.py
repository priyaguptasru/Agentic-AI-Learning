from fastapi import Request
from fastapi import HTTPException

from fastapi.responses import JSONResponse


# ----------------------------------
# HTTP EXCEPTION HANDLER
# ----------------------------------

async def http_exception_handler(
    request: Request,
    exc: HTTPException
):

    return JSONResponse(

        status_code=exc.status_code,

        content={

            "status": "error",

            "status_code": exc.status_code,

            "message": exc.detail

        }

    )