"""
Hybrid Search Service

Pipeline

1. Query Normalization
2. Query Expansion
3. Semantic Search
4. Keyword Search
5. Merge Results
6. Remove Duplicates
7. Rerank Results
"""

from app.services.keyword_search import KeywordSearchService
from app.services.query_expansion import QueryExpansionService
from app.services.query_normalizer import QueryNormalizer
from app.services.semantic_search import SemanticSearchService


class HybridSearchService:

    MAX_RESULTS = 5

    SEMANTIC_WEIGHT = 2
    KEYWORD_WEIGHT = 1

    def __init__(self):

        print("\nInitializing Hybrid Search...")

        self.normalizer = QueryNormalizer()
        self.expander = QueryExpansionService()
        self.semantic_search = SemanticSearchService()
        self.keyword_search = KeywordSearchService()

        print("Hybrid Search Ready!")

    # ---------------------------------------------------------

    def search(self, query: str):

        print("\nOriginal Query:")
        print(query)

        normalized_query = self.normalizer.normalize(query)

        print("\nNormalized Query:")
        print(normalized_query)

        expanded_query = self.expander.expand(normalized_query)

        print("\nExpanded Query:")
        print(expanded_query)

        # Semantic Search

        semantic_results = self.semantic_search.search(
            query=normalized_query,
            top_k=self.MAX_RESULTS,
        )

        # Keyword Search

        keyword_results = self.keyword_search.search(query=expanded_query)

        merged_results = {}

        # =====================================================
        # Semantic Results
        # =====================================================

        semantic_docs = semantic_results["documents"][0]
        semantic_meta = semantic_results["metadatas"][0]
        semantic_dist = semantic_results["distances"][0]

        for doc, meta, dist in zip(
            semantic_docs,
            semantic_meta,
            semantic_dist,
        ):

            similarity = round(1 / (1 + dist), 4)

            key = (
                meta["document"],
                meta["page"],
                meta["section"],
            )

            merged_results[key] = {
                "document": meta["document"],
                "page": meta["page"],
                "section": meta["section"],
                "text": doc,
                "similarity": similarity,
                "score": self.SEMANTIC_WEIGHT,
                "source": "Semantic",
            }

        # =====================================================
        # Keyword Results
        # =====================================================

        for result in keyword_results:

            key = (
                result["document"],
                result["page"],
                result["section"],
            )

            if key in merged_results:

                merged_results[key]["score"] += self.KEYWORD_WEIGHT
                merged_results[key]["source"] = "Semantic + Keyword"

            else:

                merged_results[key] = {
                    "document": result["document"],
                    "page": result["page"],
                    "section": result["section"],
                    "text": result["text"],
                    "similarity": 0.0,
                    "score": self.KEYWORD_WEIGHT,
                    "source": "Keyword",
                }

        # =====================================================
        # Final Ranking
        # =====================================================

        for result in merged_results.values():

            result["final_score"] = 0.7 * result["similarity"] + 0.3 * result["score"]

        final_results = sorted(
            merged_results.values(),
            key=lambda item: item["final_score"],
            reverse=True,
        )

        return final_results[: self.MAX_RESULTS]


# ---------------------------------------------------------

if __name__ == "__main__":

    service = HybridSearchService()

    while True:

        query = input("\nQuery : ").strip()

        if query.lower() in ["q", "quit", "exit"]:
            break

        results = service.search(query)

        print("\n")

        if not results:

            print("No results found.")
            continue

        for index, result in enumerate(results, start=1):

            print("=" * 80)

            print(f"Rank       : {index}")
            print(f"Score      : {result['score']}")
            print(f"Similarity : {result['similarity']}")
            print(f"Source     : {result['source']}")
            print(f"Document   : {result['document']}")
            print(f"Page       : {result['page']}")
            print(f"Section    : {result['section']}")

            print("\nText:\n")

            print(result["text"][:300])
