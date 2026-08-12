"""
Keyword Search Service

This service performs keyword-based search
on the stored document chunks.
"""

from pathlib import Path
import chromadb


class KeywordSearchService:

    def __init__(self):

        print("\nInitializing Keyword Search...")

        # ----------------------------------
        # Load ChromaDB
        # ----------------------------------

        BASE_DIR = Path(__file__).resolve().parents[2]

        VECTOR_DB_PATH = BASE_DIR / "vector_db"

        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))

        self.collection = self.client.get_collection(name="documents")

        print("Keyword Search Ready!")

    # ----------------------------------
    # SEARCH
    # ----------------------------------

    def search(self, query: str):

        print(f"\nSearching for keyword: {query}")

        # ----------------------------------
        # STOP WORDS
        # ----------------------------------

        stop_words = {
            "what",
            "who",
            "which",
            "where",
            "when",
            "why",
            "how",
            "is",
            "are",
            "was",
            "were",
            "do",
            "does",
            "did",
            "of",
            "for",
            "to",
            "in",
            "on",
            "with",
            "about",
            "content",
            "contain",
            "contains",
            "file",
            "pdf",
        }

        # ----------------------------------
        # SPLIT QUERY
        # ----------------------------------

        keywords = [
            word.lower() for word in query.split() if word.lower() not in stop_words
        ]

        # ----------------------------------
        # LOAD ALL DOCUMENTS
        # ----------------------------------

        data = self.collection.get(include=["documents", "metadatas"])

        documents = data["documents"]
        metadatas = data["metadatas"]

        results = []

        # ----------------------------------
        # KEYWORD MATCH
        # ----------------------------------

        for document, metadata in zip(documents, metadatas):

            text = document.lower()

            score = 0

            # Count every occurrence of every keyword
            for keyword in keywords:

                score += text.count(keyword)

            if score > 0:

                results.append(
                    {
                        "document": metadata["document"],
                        "page": metadata["page"],
                        "section": metadata["section"],
                        "text": document,
                        "score": score,
                    }
                )

        # ----------------------------------
        # REMOVE DUPLICATES
        # ----------------------------------

        unique_results = {}

        for result in results:

            key = (
                result["document"],
                result["page"],
                result["section"],
            )

            # Keep the result with the highest score
            if (
                key not in unique_results
                or result["score"] > unique_results[key]["score"]
            ):
                unique_results[key] = result

        results = list(unique_results.values())

        # ----------------------------------
        # SORT RESULTS
        # ----------------------------------

        results.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return results


# ----------------------------------
# TEST
# ----------------------------------

if __name__ == "__main__":

    service = KeywordSearchService()

    print("\n" + "=" * 80)
    print("KEYWORD DOCUMENT SEARCH")
    print("=" * 80)

    while True:

        query = input("\nEnter query (exit to quit): ").strip()

        if query.lower() in ["exit", "quit", "q"]:
            break

        results = service.search(query)

        print()

        if not results:

            print("No matching results found.")
            continue

        for index, result in enumerate(results, start=1):

            print("=" * 80)

            print(f"Result {index}")

            print(f"Score    : {result['score']}")
            print(f"Document : {result['document']}")
            print(f"Page     : {result['page']}")
            print(f"Section  : {result['section']}")

            print("\nText:\n")

            print(result["text"][:300])

            print()
