"""
Vector Store Service

This service stores document chunk embeddings
inside ChromaDB.
"""

import chromadb

from app.services.embedding_service import EmbeddingService


class VectorStoreService:

    def __init__(self):

        print("\nInitializing ChromaDB...")

        from pathlib import Path

        BASE_DIR = Path(__file__).resolve().parents[2]

        VECTOR_DB_PATH = BASE_DIR / "vector_db"

        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))

        try:
            self.client.delete_collection("documents")
            print("Old ChromaDB collection deleted.")
        except Exception:
            print("No existing collection found.")

        self.collection = self.client.create_collection(name="documents")

        print("ChromaDB Initialized Successfully!")

    # ---------------------------------------------------
    # STORE EMBEDDINGS
    # ---------------------------------------------------

    def store_embeddings(self):

        # -----------------------------------------------
        # GENERATE EMBEDDINGS
        # -----------------------------------------------

        embedding_service = EmbeddingService()

        embedded_chunks = embedding_service.generate_chunk_embeddings()

        print(f"\nProcessing {len(embedded_chunks)} chunks...")

        stored_count = 0
        skipped_count = 0

        # -----------------------------------------------
        # STORE EACH CHUNK
        # -----------------------------------------------

        for index, chunk in enumerate(embedded_chunks, start=1):

            # Create a unique ID for every chunk
            chunk_id = (
                f"{chunk['document']}"
                f"_P{chunk['page']}"
                f"_{chunk['section']}"
                f"_{index}"
            )

            # Make ID filesystem/database friendly
            chunk_id = (
                chunk_id.replace(" ", "_")
                .replace("/", "_")
                .replace("\\", "_")
                .replace(":", "_")
            )

            # # -------------------------------------------
            # # CHECK WHETHER CHUNK ALREADY EXISTS
            # # -------------------------------------------

            # existing = self.collection.get(ids=[chunk_id])

            # if existing["ids"]:

            #     skipped_count += 1

            #     print(f"Skipping Existing Chunk : {chunk_id}")

            #     continue

            # -------------------------------------------
            # STORE NEW CHUNK
            # -------------------------------------------

            self.collection.add(
                ids=[chunk_id],
                embeddings=[chunk["embedding"].tolist()],
                documents=[chunk["text"]],
                metadatas=[
                    {
                        "document": chunk["document"],
                        "page": chunk["page"],
                        "section": chunk["section"],
                    }
                ],
            )

            stored_count += 1

            print(f"Stored Chunk : {chunk_id}")

        print("\n" + "=" * 60)

        print("VECTOR STORE SUMMARY")

        print("=" * 60)

        print(f"Total Chunks     : {len(embedded_chunks)}")

        print(f"New Stored       : {stored_count}")

        print(f"Skipped Existing : {skipped_count}")

        print(f"Collection Count : {self.collection.count()}")

        print("=" * 60)


# ---------------------------------------------------
# TEST
# ---------------------------------------------------

if __name__ == "__main__":

    service = VectorStoreService()

    service.store_embeddings()
