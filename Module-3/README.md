# Module-3: Frontend Development

## Overview

Module-3 provides the frontend interface for the Agentic AI project. It allows users to interact with the FastAPI backend through a simple web interface instead of using Swagger.

The frontend is built using HTML, CSS, and JavaScript and communicates with the backend using REST APIs.

---

## Features

- Upload PDF files
- Upload CSV files
- Display upload status
- Browse processed documents
- View extracted document content
- Browse processed CSV files
- View CSV records in table format
- Search documents
- Search CSV files
- Loading indicators
- Error handling
- Retry mechanism
- Responsive UI

---

## Project Structure

```
Module-3/
│
├── html/
│   ├── index.html
│   ├── documents.html
│   └── csv.html
│
├── css/
│   ├── style.css
│   ├── documents.css
│   └── csv.css
│
├── js/
│   ├── api.js
│   ├── upload.js
│   ├── documents.js
│   └── csv.js
│
├── README.md
└── .gitignore
```

---

## Technologies Used

- HTML5
- CSS3
- JavaScript (ES6)
- Fetch API
- FastAPI (Backend)
- PostgreSQL

---

## Backend Requirements

Module-2 must be running before starting Module-3.

Start the backend:

```bash
uvicorn app.main:app --reload
```

Backend URL:

```
http://127.0.0.1:8000
```

Swagger:

```
http://127.0.0.1:8000/docs
```

---

## Running the Frontend

Navigate to Module-3:

```bash
cd Module-3
```

Start a local server:

```bash
python -m http.server 5500
```

Open:

```
http://127.0.0.1:5500/html/index.html
```

---

## Available Pages

### Home

```
index.html
```

Features:

- Upload PDF
- Upload CSV
- Upload Status
- Navigation

---

### Documents

```
documents.html
```

Features:

- View processed documents
- Search documents
- View extracted pages
- View sections
- View paragraphs

---

### CSV Browser

```
csv.html
```

Features:

- View CSV files
- Search CSV files
- Display CSV records
- Table view

---

## API Integration

The frontend communicates with the following APIs:

### Upload

```
POST /ingest/pdf

POST /ingest/csv
```

### Documents

```
GET /documents

GET /documents/{id}

GET /documents/{id}/content
```

### CSV

```
GET /csv/files

GET /csv/files/{id}

GET /csv/files/{id}/records
```

---

## Frontend Architecture

```
User

↓

HTML

↓

JavaScript

↓

Fetch API

↓

FastAPI

↓

PostgreSQL
```

---

## Error Handling

Implemented:

- Loading messages
- API error messages
- Retry buttons
- Upload validation
- Disabled upload button during processing

---

## Future Enhancements

- Authentication
- User Login
- Ticket Management
- Dashboard Analytics
- File Download
- Pagination
- Dark Mode

---

## Author

Priya Gupta