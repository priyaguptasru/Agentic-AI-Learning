# Module-2: Backend Development

## Project Overview

Module-2 is a FastAPI-based backend application that exposes REST APIs for document and CSV ingestion. It validates uploaded files, executes long-running tasks asynchronously, and orchestrates the complete data engineering pipeline implemented in Module-1.

The backend receives uploaded files, stores them temporarily, copies them to Module-1 for processing, and triggers the extraction, transformation, normalization, and database loading pipeline.

---

## Features

* REST APIs for PDF and CSV ingestion
* File upload validation
* Duplicate file validation
* File size validation
* Background task execution using FastAPI `BackgroundTasks`
* Integration with Module-1 ETL pipeline
* PostgreSQL integration
* SQLAlchemy ORM
* Swagger API documentation
* Error handling with HTTP exceptions
* Service-oriented architecture

---

## Project Structure

```
Module-2
│
├── app
│   ├── core
│   │   └── database.py
│   │
│   ├── models
│   │   ├── document.py
│   │   ├── page.py
│   │   ├── section.py
│   │   ├── paragraph.py
│   │   ├── csv_file.py
│   │   └── csv_record.py
│   │
│   ├── routers
│   │   ├── ingestion.py
│   │   ├── document.py
│   │   └── csv.py
│   │
│   ├── schemas
│   │   ├── document_schema.py
│   │   ├── csv_file_schema.py
│   │   └── csv_record_schema.py
│   │
│   ├── services
│   │   ├── ingestion_service.py
│   │   └── pipeline_service.py
│   │
│   ├── utils
│   │   ├── file_validator.py
│   │   └── file_transfer.py
│   │
│   └── main.py
│
├── uploads
│   ├── pdfs
│   └── csvs
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Technology Stack

* Python 3.12
* FastAPI
* SQLAlchemy
* PostgreSQL
* Uvicorn
* Pydantic
* Swagger / OpenAPI

---

## API Endpoints

### Health Check

```
GET /
```

Returns application status.

---

### Upload PDF

```
POST /ingest/pdf
```

Uploads a PDF document, validates the file, stores it, and triggers the Module-1 PDF processing pipeline asynchronously.

---

### Upload CSV

```
POST /ingest/csv
```

Uploads a CSV file, validates the file, stores it, and triggers the Module-1 CSV processing pipeline asynchronously.

---

### Document APIs

```
GET /documents
```

Returns all processed documents.

```
GET /documents/{document_id}
```

Returns metadata for a specific document.

```
GET /documents/{document_id}/content
```

Returns pages, sections, and paragraphs for a document.

---

### CSV APIs

```
GET /csv-files
```

Returns all uploaded CSV files.

```
GET /csv-files/{file_id}
```

Returns all records belonging to the selected CSV file.

---

## Execution Flow

```
Client
    │
    ▼
FastAPI Upload API
    │
    ▼
Validation
    │
    ▼
Store File
    │
    ▼
Background Task
    │
    ▼
Copy File to Module-1
    │
    ▼
Module-1 Pipeline
    │
    ├── PDF Extraction
    ├── Document Structure Detection
    ├── JSON Normalization
    ├── CSV Cleaning
    └── PostgreSQL Loading
    │
    ▼
Database
```

---

## Running the Project

### Activate Virtual Environment

```
.\.venv2\Scripts\Activate
```

### Install Dependencies

```
pip install -r requirements.txt
```

### Run FastAPI

```
uvicorn app.main:app --reload
```

---

## API Documentation

After starting the application, open:

```
http://127.0.0.1:8000/docs
```

Swagger UI provides interactive documentation for all REST APIs.

---

## Validation

The backend performs the following validations:

* Only PDF files are accepted for PDF ingestion.
* Only CSV files are accepted for CSV ingestion.
* Duplicate files are rejected.
* File size validation is performed.
* Appropriate HTTP error responses are returned.

---

## Database

The application uses PostgreSQL with SQLAlchemy ORM.

Processed data includes:

* Documents
* Pages
* Sections
* Paragraphs
* CSV Files
* CSV Records

---

## Module Integration

Module-2 does not perform data extraction itself.

Instead, it orchestrates the Module-1 ETL pipeline by:

1. Receiving uploaded files.
2. Validating uploads.
3. Copying files into Module-1 input folders.
4. Triggering the Module-1 processing pipeline.
5. Returning API responses immediately while processing continues in the background.

---

## Author

Priya Gupta

```
```
