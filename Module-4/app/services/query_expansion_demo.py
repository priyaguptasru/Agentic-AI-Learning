"""
Query Expansion Demo

This service compares retrieval results:

1. Without Query Expansion
2. With Query Expansion

using Semantic Search.
"""

from app.services.semantic_search import SemanticSearchService
from app.services.query_normalizer import QueryNormalizer
from app.services.query_expansion import QueryExpansionService


class QueryExpansionDemo:

    def __init__(self):

        print("\nInitializing Query Expansion Demo...")

        self.semantic = SemanticSearchService()

        self.normalizer = QueryNormalizer()

        self.expander = QueryExpansionService()

        print("Query Expansion Demo Ready!")

    # ----------------------------------
    # DEMO
    # ----------------------------------

    def compare(self, query: str):

        print("\n")
        print("=" * 80)
        print("QUERY EXPANSION DEMO")
        print("=" * 80)

        print(f"\nOriginal Query : {query}")

        normalized_query = self.normalizer.normalize(query)

        expanded_query = self.expander.expand(normalized_query)

        print(f"\nNormalized Query : {normalized_query}")

        print(f"\nExpanded Query : {expanded_query}")

        # ----------------------------------
        # WITHOUT QUERY EXPANSION
        # ----------------------------------

        print("\n")
        print("=" * 80)
        print("WITHOUT QUERY EXPANSION")
        print("=" * 80)

        without_results = self.semantic.search(query=normalized_query, top_k=1)

        metadata = without_results["metadatas"][0][0]

        distance = without_results["distances"][0][0]

        similarity = round(1 / (1 + distance), 4)

        print(f"Document : {metadata['document']}")
        print(f"Page : {metadata['page']}")
        print(f"Section : {metadata['section']}")
        print(f"Similarity : {similarity}")

        # ----------------------------------
        # WITH QUERY EXPANSION
        # ----------------------------------

        print("\n")
        print("=" * 80)
        print("WITH QUERY EXPANSION")
        print("=" * 80)

        with_results = self.semantic.search(query=expanded_query, top_k=1)

        metadata = with_results["metadatas"][0][0]

        distance = with_results["distances"][0][0]

        similarity = round(1 / (1 + distance), 4)

        print(f"Document : {metadata['document']}")
        print(f"Page : {metadata['page']}")
        print(f"Section : {metadata['section']}")
        print(f"Similarity : {similarity}")

        # ----------------------------------
        # OBSERVATION
        # ----------------------------------

        print("\n")
        print("=" * 80)
        print("OBSERVATION")
        print("=" * 80)

        print(
            "Query Expansion enriches the search query "
            "with related terms. This helps retrieve "
            "additional relevant chunks and improves "
            "overall recall while preserving semantic meaning."
        )


# ----------------------------------
# TEST
# ----------------------------------

if __name__ == "__main__":

    demo = QueryExpansionDemo()

    demo.compare("What is Routing?")
