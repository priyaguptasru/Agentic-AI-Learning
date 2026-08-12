"""
Embedding Service

This service generates vector embeddings
for document chunks.
"""

from sentence_transformers import SentenceTransformer

from app.services.chunking import ChunkingService


class EmbeddingService:

    def __init__(self):

        print("\nLoading Embedding Model...")

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Embedding Model Loaded Successfully!")

    # ----------------------------------
    # GENERATE SINGLE EMBEDDING
    # ----------------------------------

    def generate_embedding(self, text: str):

        return self.model.encode(
            text,
            convert_to_numpy=True, 
            normalize_embeddings=True,
        )

    # ----------------------------------
    # GENERATE EMBEDDINGS FOR ALL CHUNKS
    # ----------------------------------

    def generate_chunk_embeddings(self):

        chunk_service = ChunkingService()

        chunks = chunk_service.create_chunks()

        embedded_chunks = []

        print(f"\nTotal Chunks : {len(chunks)}")

        for index, chunk in enumerate(chunks, start=1):

            embedding = self.generate_embedding(chunk["text"])

            chunk["embedding"] = embedding

            embedded_chunks.append(chunk)

            print(f"Chunk {index} -> Embedding Length : {len(embedding)}")

        return embedded_chunks


# ----------------------------------
# TEST
# ----------------------------------

if __name__ == "__main__":

    service = EmbeddingService()

    embedded_chunks = service.generate_chunk_embeddings()

    print(f"\nTotal Embedded Chunks : {len(embedded_chunks)}")

    print("\nSample Chunk")

    print("=" * 60)

    print(embedded_chunks[0]["document"])
    print(embedded_chunks[0]["page"])
    print(embedded_chunks[0]["section"])

    print("\nText:\n")

    print(embedded_chunks[0]["text"][:200])

    print(f"\nEmbedding Length : {len(embedded_chunks[0]['embedding'])}")
