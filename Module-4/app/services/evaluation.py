"""
Evaluation Service

Compares the performance of:

1. Semantic Search
2. Keyword Search
3. Hybrid Search

Evaluation Metrics
------------------
- Retrieval Time
- Top Results
- Similarity
- Keyword Score
- Hybrid Score
- Average Statistics
"""

import time

from app.services.semantic_search import SemanticSearchService
from app.services.keyword_search import KeywordSearchService
from app.services.hybrid_search import HybridSearchService


class EvaluationService:

    TOP_K = 3

    def __init__(self):

        print("\nInitializing Evaluation Service...")

        self.semantic = SemanticSearchService()
        self.keyword = KeywordSearchService()
        self.hybrid = HybridSearchService()

        print("Evaluation Service Ready!")

    # ---------------------------------------------------------
    # RUN EVALUATION
    # ---------------------------------------------------------

    def evaluate(self):

        print("\nEnter evaluation queries.")
        print("Type 'done' when finished.\n")

        queries = []

        while True:

            query = input("Query : ").strip()

            if query.lower() == "done":
                break

            if query:
                queries.append(query)

        if not queries:

            print("\nNo queries entered.")
            return

        # -----------------------------------------------------
        # Summary Statistics
        # -----------------------------------------------------

        semantic_times = []
        keyword_times = []
        hybrid_times = []

        semantic_similarities = []
        keyword_scores = []
        hybrid_scores = []

        print("\n")
        print("=" * 100)
        print("RETRIEVAL EVALUATION")
        print("=" * 100)

        for query in queries:

            print("\n")
            print("=" * 100)
            print(f"Query : {query}")
            print("=" * 100)

            # =====================================================
            # Semantic Search
            # =====================================================

            start = time.perf_counter()

            semantic_results = self.semantic.search(
                query=query,
                top_k=self.TOP_K,
            )

            semantic_time = time.perf_counter() - start
            semantic_times.append(semantic_time)

            print("\nSemantic Search")
            print(f"Retrieval Time : {semantic_time:.4f} sec")

            semantic_docs = semantic_results["documents"][0]

            if semantic_docs:

                print(f"Results Found  : {len(semantic_docs)}")

                for index in range(len(semantic_docs)):

                    metadata = semantic_results["metadatas"][0][index]
                    distance = semantic_results["distances"][0][index]

                    similarity = round(1 / (1 + distance), 4)

                    semantic_similarities.append(similarity)

                    print(f"\nResult {index + 1}")

                    print(f"Document   : {metadata['document']}")
                    print(f"Page       : {metadata['page']}")
                    print(f"Section    : {metadata['section']}")
                    print(f"Similarity : {similarity}")

            else:

                print("No Results Found")

            # =====================================================
            # Keyword Search
            # =====================================================

            start = time.perf_counter()

            keyword_results = self.keyword.search(query=query)

            keyword_time = time.perf_counter() - start
            keyword_times.append(keyword_time)

            print("\nKeyword Search")
            print(f"Retrieval Time : {keyword_time:.4f} sec")

            if keyword_results:

                print(f"Results Found  : {len(keyword_results)}")

                for index, result in enumerate(keyword_results[: self.TOP_K], start=1):

                    keyword_scores.append(result["score"])

                    print(f"\nResult {index}")

                    print(f"Document      : {result['document']}")
                    print(f"Page          : {result['page']}")
                    print(f"Section       : {result['section']}")
                    print(f"Keyword Score : {result['score']}")

            else:

                print("No Results Found")

            # =====================================================
            # Hybrid Search
            # =====================================================

            start = time.perf_counter()

            hybrid_results = self.hybrid.search(query=query)

            hybrid_time = time.perf_counter() - start
            hybrid_times.append(hybrid_time)

            print("\nHybrid Search")
            print(f"Retrieval Time : {hybrid_time:.4f} sec")

            if hybrid_results:

                print(f"Results Found  : {len(hybrid_results)}")

                for index, result in enumerate(hybrid_results[: self.TOP_K], start=1):

                    hybrid_scores.append(result["score"])

                    print(f"\nResult {index}")

                    print(f"Document   : {result['document']}")
                    print(f"Page       : {result['page']}")
                    print(f"Section    : {result['section']}")
                    print(f"Score      : {result['score']}")
                    print(f"Similarity : {result['similarity']}")
                    print(f"Source     : {result['source']}")

            else:

                print("No Results Found")

            print("\n" + "-" * 100)

        # =====================================================
        # SUMMARY
        # =====================================================

        print("\n")
        print("=" * 100)
        print("EVALUATION SUMMARY")
        print("=" * 100)

        if semantic_times:
            print(
                f"\nAverage Semantic Retrieval Time : {sum(semantic_times)/len(semantic_times):.4f} sec"
            )

        if keyword_times:
            print(
                f"Average Keyword Retrieval Time : {sum(keyword_times)/len(keyword_times):.4f} sec"
            )

        if hybrid_times:
            print(
                f"Average Hybrid Retrieval Time  : {sum(hybrid_times)/len(hybrid_times):.4f} sec"
            )

        if semantic_similarities:
            print(
                f"\nAverage Semantic Similarity    : {sum(semantic_similarities)/len(semantic_similarities):.4f}"
            )

        if keyword_scores:
            print(
                f"Average Keyword Score          : {sum(keyword_scores)/len(keyword_scores):.2f}"
            )

        if hybrid_scores:
            print(
                f"Average Hybrid Score           : {sum(hybrid_scores)/len(hybrid_scores):.2f}"
            )


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    service = EvaluationService()

    service.evaluate()
