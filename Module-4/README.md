# Module-4 : Retrieval Systems & Query Intelligence

## Objective

Build an enterprise Retrieval System capable of retrieving the most relevant document chunks using:

- Structure-aware Chunking
- Embedding Generation
- Vector Database (ChromaDB)
- Semantic Search
- Keyword Search
- Hybrid Search
- Query Normalization
- Query Expansion
- Re-ranking
- Retrieval Evaluation

---

# Project Structure

```
Module-4
│
├── app
│   └── services
│       ├── chunking.py
│       ├── embedding_service.py
│       ├── vector_store.py
│       ├── semantic_search.py
│       ├── keyword_search.py
│       ├── hybrid_search.py
│       ├── query_normalizer.py
│       ├── query_expansion.py
│       ├── query_expansion_demo.py
│       ├── evaluation.py
│       └── charts.py
│
├── vector_db
│
├── output
│   ├── charts
│   └── comparison_report.md
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Technologies Used

- Python 3.12
- ChromaDB
- Sentence Transformers
- HuggingFace
- SQLAlchemy
- PostgreSQL
- Matplotlib
- NumPy

---

# Installation

## Clone Repository

```bash
git clone <repository_url>
cd Module-4
```

## Create Virtual Environment

```bash
python -m venv .venv4
```

Activate

### Windows

```bash
.venv4\Scripts\activate
```

### Linux/Mac

```bash
source .venv4/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Features

## 1. Chunking

Splits extracted document text into semantically meaningful chunks.

Run

```bash
python -m app.services.chunking
```

---

## 2. Embedding Generation

Generates dense vector embeddings using Sentence Transformers.

Run

```bash
python -m app.services.embedding_service
```

---

## 3. Vector Store

Stores embeddings in ChromaDB.

Run

```bash
python -m app.services.vector_store
```

---

## 4. Semantic Search

Performs embedding-based similarity search.

Run

```bash
python -m app.services.semantic_search
```

---

## 5. Keyword Search

Performs keyword matching over document chunks.

Run

```bash
python -m app.services.keyword_search
```

---

## 6. Hybrid Search

Combines Semantic and Keyword Search with simple re-ranking.

Run

```bash
python -m app.services.hybrid_search
```

---

## 7. Query Normalization

Normalizes user queries.

Examples

- Lowercase conversion
- Remove punctuation
- Remove extra spaces

Run

```bash
python -m app.services.query_normalizer
```

---

## 8. Query Expansion

Expands queries using predefined synonyms and aliases.

Run

```bash
python -m app.services.query_expansion
```

---

## 9. Evaluation

Compares retrieval strategies.

Run

```bash
python -m app.services.evaluation
```

---

## 10. Charts

Generates:

- Similarity Comparison
- Retrieval Comparison
- Retrieval Pipeline

Run

```bash
python -m app.services.charts
```

Charts are saved under

```
output/charts/
```

---

# Generated Outputs

```
output/
│
├── charts
│   ├── similarity_comparison.png
│   ├── retrieval_comparison.png
│   └── pipeline_flow.png
│
└── comparison_report.md
```

---

# Retrieval Pipeline

```
User Query
      │
      ▼
Normalize Query
      │
      ▼
Expand Query
      │
      ▼
Semantic Search
      │
      ├────────► Keyword Search
      │
      ▼
Hybrid Search
      │
      ▼
Re-ranking
      │
      ▼
Final Results
```

---

# Module Completion

Implemented Features

- Structure-aware Chunking
- Embedding Generation
- ChromaDB Vector Store
- Semantic Search
- Keyword Search
- Hybrid Search
- Query Normalization
- Query Expansion
- Result Re-ranking
- Retrieval Evaluation
- Performance Visualization

---

# Author

Developed as part of the **Agentic AI Learning Program – Module-4** focusing on Retrieval Systems & Query Intelligence.
