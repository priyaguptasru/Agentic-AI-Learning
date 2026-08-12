"""
Semantic Search Service

This service performs semantic search
using ChromaDB and Sentence Transformers.
"""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


class SemanticSearchService:

    # Debug threshold
    SIMILARITY_THRESHOLD = 0.30

    def __init__(self):

        print("\nInitializing Semantic Search...")

        BASE_DIR = Path(__file__).resolve().parents[2]
        VECTOR_DB_PATH = BASE_DIR / "vector_db"

        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))

        self.collection = self.client.get_collection(name="documents")

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Semantic Search Ready!")

    # ----------------------------------
    # SEARCH
    # ----------------------------------

    def search(self, query: str, top_k: int = 5):

        print(f"\nSearching for:\n{query}")

        query_embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
        )

        filtered_documents = []
        filtered_metadatas = []
        filtered_distances = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        print("\nSemantic Search Scores\n")

        for doc, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):

            similarity = 1 / (1 + distance)

            print(f"Raw Distance : {distance:.4f} | " f"Similarity : {similarity:.4f}")

            if similarity >= self.SIMILARITY_THRESHOLD:

                filtered_documents.append(doc)
                filtered_metadatas.append(metadata)
                filtered_distances.append(distance)

        return {
            "documents": [filtered_documents],
            "metadatas": [filtered_metadatas],
            "distances": [filtered_distances],
        }


# ----------------------------------
# TEST
# ----------------------------------

if __name__ == "__main__":

    service = SemanticSearchService()

    print("\n" + "=" * 80)
    print("SEMANTIC DOCUMENT SEARCH")
    print("=" * 80)
    print("Type your question below.")
    print("Type 'exit' to quit.")
    print("=" * 80)

    while True:

        query = input("\nEnter your query : ").strip()

        if query.lower() == "exit":

            print("\nExiting Semantic Search...")
            break

        if not query:

            print("Please enter a valid query.")
            continue

        results = service.search(query)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        print("\n")
        print("=" * 80)
        print("SEMANTIC SEARCH RESULTS")
        print("=" * 80)

        if not documents:

            print("\nNo matching results found.")
            continue

        for i in range(len(documents)):

            similarity = 1 / (1 + distances[i])

            print(f"\nResult {i + 1}")
            print(f"Similarity : {similarity:.4f}")
            print(f"Document   : {metadatas[i]['document']}")
            print(f"Page       : {metadatas[i]['page']}")
            print(f"Section    : {metadatas[i]['section']}")

            print("\nText:\n")

            print(documents[i][:300])

            print("\n" + "=" * 80)
