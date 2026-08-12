# Entity Relationships and Traceability

## Entities

1. Document
2. Page
3. Section
4. Paragraph

---

## Relationship 1

Document → Page

Relationship Type:
One-to-Many (1:N)

Explanation:
A single document can contain multiple pages.

Example:

AI_Paper.pdf

* Page 1
* Page 2
* Page 3

---

## Relationship 2

Page → Section

Relationship Type:
One-to-Many (1:N)

Explanation:
A single page can contain multiple sections.

Example:

Page 1

* Introduction
* Background
* Conclusion

---

## Relationship 3

Section → Paragraph

Relationship Type:
One-to-Many (1:N)

Explanation:
A single section can contain multiple paragraphs.

Example:

Introduction

* Paragraph 1
* Paragraph 2
* Paragraph 3

---

## Data Flow

Document
↓
Page
↓
Section
↓
Paragraph

---

## Traceability Flow

Paragraph
↓
Section
↓
Page
↓
Document

This hierarchy allows any extracted answer to be traced back to its original source document, page, section, and paragraph.
