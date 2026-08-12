"""
Chunking Service

Creates production-quality chunks for RAG.

Features:
1. Reads documents from PostgreSQL
2. Stops after References/Bibliography
3. Splits long text into overlapping chunks
4. Merges very small chunks with previous chunk
5. Returns clean chunks for embedding
"""

import os
import re
import sys
from collections import Counter

from app.database.db import SessionLocal

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
MODULE4_DIR = os.path.dirname(APP_DIR)
PROJECT_ROOT = os.path.dirname(MODULE4_DIR)

MODULE1_DIR = os.path.join(PROJECT_ROOT, "Module-1")

if MODULE1_DIR not in sys.path:
    sys.path.append(MODULE1_DIR)

from models.document import Document
from models.page import Page
from models.section import Section
from models.paragraph import Paragraph


class ChunkingService:

    def __init__(self):

        self.db = SessionLocal()

        # Sections that terminate document processing.
        # Empty set means process the complete document.
        self.stop_sections = set()

        self.chunk_size = 800
        self.chunk_overlap = 150
        self.minimum_chunk_length = 120

    # -------------------------------------------------

    def clean_text(self, text: str):

        if not text:
            return ""

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # -------------------------------------------------

    def split_text(self, text):

        chunks = []

        start = 0

        text_length = len(text)

        while start < text_length:

            end = min(start + self.chunk_size, text_length)

            # ---------------------------------------
            # Avoid cutting words in half
            # ---------------------------------------

            if end < text_length:

                last_space = text.rfind(" ", start, end)

                if last_space > start:

                    end = last_space

            chunk = text[start:end].strip()

            if chunk:

                chunks.append(chunk)

            # ---------------------------------------
            # Finished
            # ---------------------------------------

            if end >= text_length:

                break

            # ---------------------------------------
            # Maintain overlap
            # ---------------------------------------

            start = max(end - self.chunk_overlap, 0)

        return chunks

    # -------------------------------------------------

    def create_chunks(self):

        chunks = []

        skipped_small = 0
        merged_small = 0
        stopped_documents = 0

        documents = self.db.query(Document).all()

        print("\nCreating Chunks...\n")

        for document in documents:

            print(f"Processing Document : {document.document_name}")

            stop_processing = False

            for page in document.pages:

                if stop_processing:
                    break

                for section in page.sections:

                    header = section.header.strip() if section.header else ""

                    header_lower = header.lower()

                    if header_lower in self.stop_sections:

                        print(f"Stopping after section: {header}")

                        stop_processing = True
                        stopped_documents += 1
                        break

                    text = ""

                    for paragraph in section.paragraphs:

                        if paragraph.text:
                            text += paragraph.text + "\n"

                    text = self.clean_text(text)

                    if not text:
                        continue

                    previous_chunk = None

                    for piece in self.split_text(text):

                        # ------------------------------------------
                        # Merge very small chunks with previous chunk
                        # ------------------------------------------

                        if len(piece) < self.minimum_chunk_length:

                            if previous_chunk is not None:

                                previous_chunk["text"] += "\n" + piece

                                merged_small += 1

                                print(
                                    f"Merged small chunk ({len(piece)} chars) "
                                    f"into previous chunk."
                                )

                            else:

                                skipped_small += 1

                            continue

                        current_chunk = {
                            "document": document.document_name,
                            "page": page.page_number,
                            "section": header,
                            "text": piece,
                        }

                        chunks.append(current_chunk)

                        previous_chunk = current_chunk

        print("\n" + "=" * 60)
        print("CHUNKING SUMMARY")
        print("=" * 60)
        print(f"Total Chunks        : {len(chunks)}")
        print(f"Stopped Documents   : {stopped_documents}")
        print(f"Merged Small Chunks : {merged_small}")
        print(f"Skipped Small Chunk : {skipped_small}")
        print("\nChunks Per Document")
        print("-" * 60)

        document_counts = Counter(chunk["document"] for chunk in chunks)

        for document_name, count in document_counts.items():

            print(f"{document_name:<30} : {count}")

        print("=" * 60)

        return chunks


# -------------------------------------------------

if __name__ == "__main__":

    service = ChunkingService()

    chunks = service.create_chunks()

    print(f"\nGenerated {len(chunks)} chunks")

    for i, chunk in enumerate(chunks[:10], start=1):

        print("\n" + "=" * 70)
        print(f"Chunk {i}")
        print(f"Document : {chunk['document']}")
        print(f"Page     : {chunk['page']}")
        print(f"Section  : {chunk['section']}")
        print(f"Length   : {len(chunk['text'])}")

        print("\nPreview:\n")

        print(chunk["text"][:300])
