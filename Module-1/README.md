# Module-1: Data Engineering Pipeline for Agentic AI

## Overview

This module demonstrates an end-to-end data engineering pipeline for preparing unstructured and semi-structured data for AI applications. The project extracts content from PDF documents, cleans CSV datasets, converts extracted information into structured JSON, and stores everything in PostgreSQL using SQLAlchemy ORM.

The implementation follows a modular, production-oriented approach with logging, error handling, and duplicate prevention.

---

# Objectives

* Extract text from multiple PDF documents.
* Detect document structure (pages, sections, headers, paragraphs).
* Explore and clean CSV datasets.
* Normalize extracted content into structured JSON.
* Store PDF and CSV data in PostgreSQL.
* Implement SQLAlchemy ORM models.
* Handle partial failures gracefully.
* Maintain traceability from database records back to the original document.

---

# Project Structure

```text
Module-1
│
├── data
│   ├── pdfs
│   └── csvs
│
├── docs
│
├── models
│   ├── session.py
│   ├── document.py
│   ├── page.py
│   ├── section.py
│   ├── paragraph.py
│   ├── csv_file.py
│   └── csv_record.py
│
├── output
│   ├── text
│   ├── json
│   ├── normalized_json
│   ├── cleaned_csv
│   └── logs
│
├── scripts
│   ├── extract_all_pdfs.py
│   ├── detect_document_structure.py
│   ├── explore_csvs.py
│   ├── clean_csv_data.py
│   ├── normalize_json.py
│   ├── load_json_to_db.py
│   ├── load_csv_to_db.py
│   ├── logger.py
│   └── test_logger.py
│
├── requirements.txt
└── README.md
```

---

# Technologies Used

* Python 3.12
* PostgreSQL
* SQLAlchemy ORM
* PyMuPDF (fitz)
* Pandas
* Psycopg2
* Virtual Environment (venv)

---

# Installation

## 1. Clone the Project

```bash
git clone <repository-url>
cd Module-1
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

### Windows

```bash
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Database Setup

Create a PostgreSQL database.

Example:

```sql
CREATE DATABASE module1_db;
```

Update the database connection string inside your SQLAlchemy session configuration if required.

---

# Execution Flow

Execute the scripts in the following order.

---

## Step 1: Extract PDF Text

```bash
python -m scripts.extract_all_pdfs
```

Output:

```
output/text/
```

---

## Step 2: Detect Document Structure

```bash
python -m scripts.detect_document_structure
```

Output:

```
output/json/
```

---

## Step 3: Normalize JSON

```bash
python -m scripts.normalize_json
```

Output:

```
output/normalized_json/
```

---

## Step 4: Explore CSV Files

```bash
python -m scripts.explore_csvs
```

Displays:

* Rows
* Columns
* Data Types
* Missing Values

---

## Step 5: Clean CSV Data

```bash
python -m scripts.clean_csv_data
```

Output:

```
output/cleaned_csv/
```

Report:

```
output/logs/data_quality_report.txt
```

---

## Step 6: Create Database Tables

```bash
python -m scripts.create_tables
```

---

## Step 7: Load PDF Data into PostgreSQL

```bash
python -m scripts.load_json_to_db
```

Data is stored in:

* documents
* pages
* sections
* paragraphs

Duplicate documents are automatically skipped.

---

## Step 8: Load CSV Data into PostgreSQL

```bash
python -m scripts.load_csv_to_db
```

Data is stored in:

* csv_files
* csv_records

Duplicate CSV files are automatically skipped.

---

# Database Schema

## PDF Tables

```
documents
    │
    └── pages
            │
            └── sections
                    │
                    └── paragraphs
```

---

## CSV Tables

```
csv_files
      │
      └── csv_records
```

---

# Logging

Application logs are written to:

```
output/logs/error_log.txt
```

Examples of handled failures:

* Corrupt PDF
* Invalid JSON
* CSV read failure
* Database insertion failure
* File save failure

---

# Features

* PDF text extraction
* Document structure detection
* JSON normalization
* CSV profiling
* CSV cleaning
* PostgreSQL persistence
* SQLAlchemy ORM
* Duplicate prevention
* Error logging
* Modular architecture

---

# Traceability

Every paragraph stored in PostgreSQL can be traced back to:

```
Document
    ↓
Page
    ↓
Section
    ↓
Paragraph
```

This design enables reliable source attribution for AI-generated responses.

---

# Demo Steps

1. Add PDF files to `data/pdfs`.
2. Add CSV files to `data/csvs`.
3. Execute the scripts in order.
4. Verify generated outputs in the `output` folder.
5. Load data into PostgreSQL.
6. Execute SQL queries to verify stored data.

Example:

```sql
SELECT * FROM documents;

SELECT COUNT(*) FROM paragraphs;

SELECT * FROM csv_files;

SELECT COUNT(*) FROM csv_records;
```

---

# Future Enhancements

* OCR support for scanned PDFs.
* Automatic table extraction from PDFs.
* Image extraction.
* REST API integration (Module-2).
* AI-based semantic document search.
* Background job processing.
* Cloud storage integration.

---

# Author

Priya Gupta

Python Developer
