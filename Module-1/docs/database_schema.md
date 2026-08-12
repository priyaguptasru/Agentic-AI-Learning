TABLE: documents
- document_id (Primary Key)
- document_name

TABLE: pages
- page_id (Primary Key)
- document_id (Foreign Key)
- page_number

TABLE: sections
- section_id (Primary Key)
- page_id (Foreign Key)
- header

TABLE: paragraphs
- paragraph_id (Primary Key)
- section_id (Foreign Key)
- text