from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from app.routers.ingestion import (
    router as ingestion_router
)

from app.routers.document import (
    router as document_router
)

from app.routers.csv import (
    router as csv_router
)

from app.core.exception_handler import (
    http_exception_handler
)


app = FastAPI(
    title="Agentic AI Backend",
    version="1.0.0",
    description="Module-2 Backend Development APIs"
)


# ----------------------------------
# CORS CONFIGURATION
# ----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(
    HTTPException,
    http_exception_handler
)


# ----------------------------------
# REGISTER ROUTERS
# ----------------------------------

app.include_router(
    ingestion_router
)

app.include_router(
    document_router
)

app.include_router(
    csv_router
)

# ----------------------------------
# HEALTH CHECK
# ----------------------------------

@app.get("/")
def health_check():

    return {
        "status": "success",
        "message": "Backend is running"
    }