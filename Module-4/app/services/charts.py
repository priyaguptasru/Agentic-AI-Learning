"""
Charts Service

This service generates charts for Module-4.

Charts:
1. Similarity Comparison
2. Retrieval Comparison
3. Retrieval Pipeline
"""

import os
import matplotlib.pyplot as plt


class ChartsService:

    def __init__(self):

        self.output_dir = os.path.join(os.getcwd(), "output", "charts")

        os.makedirs(self.output_dir, exist_ok=True)

    # ----------------------------------
    # SIMILARITY COMPARISON
    # ----------------------------------

    def similarity_chart(self):

        search_types = ["Semantic", "Keyword", "Hybrid"]

        similarity_scores = [0.509, 0.31, 0.681]

        plt.figure(figsize=(8, 5))

        plt.bar(search_types, similarity_scores)

        plt.title("Similarity Comparison")
        plt.xlabel("Search Strategy")
        plt.ylabel("Similarity Score")

        plt.ylim(0, 1)

        output_file = os.path.join(self.output_dir, "similarity_comparison.png")

        plt.savefig(output_file)
        plt.close()

        print("\nSimilarity chart saved successfully.")
        print(output_file)

    # ----------------------------------
    # RETRIEVAL COMPARISON
    # ----------------------------------

    def retrieval_chart(self):

        search_types = ["Semantic", "Keyword", "Hybrid"]

        retrieved_results = [5, 16, 17]

        plt.figure(figsize=(8, 5))

        plt.bar(search_types, retrieved_results)

        plt.title("Retrieved Results Comparison")
        plt.xlabel("Search Strategy")
        plt.ylabel("Number of Results")

        output_file = os.path.join(self.output_dir, "retrieval_comparison.png")

        plt.savefig(output_file)
        plt.close()

        print("\nRetrieval comparison chart saved successfully.")
        print(output_file)

    # ----------------------------------
    # RETRIEVAL PIPELINE
    # ----------------------------------

    def pipeline_chart(self):

        plt.figure(figsize=(6, 10))

        plt.axis("off")

        steps = [
            "User Query",
            "Normalize Query",
            "Expand Query",
            "Semantic Search",
            "Keyword Search",
            "Hybrid Merge",
            "Re-ranking",
            "Final Results",
        ]

        y = 0.95

        for step in steps:

            plt.text(
                0.5,
                y,
                step,
                ha="center",
                va="center",
                fontsize=12,
                bbox=dict(boxstyle="round", fill=False),
            )

            if step != steps[-1]:

                plt.annotate(
                    "",
                    xy=(0.5, y - 0.05),
                    xytext=(0.5, y - 0.01),
                    arrowprops=dict(arrowstyle="->"),
                )

            y -= 0.10

        output_file = os.path.join(self.output_dir, "pipeline_flow.png")

        plt.savefig(output_file)
        plt.close()

        print("\nPipeline flow chart saved successfully.")
        print(output_file)


# ----------------------------------
# TEST
# ----------------------------------

if __name__ == "__main__":

    service = ChartsService()

    service.similarity_chart()

    service.retrieval_chart()

    service.pipeline_chart()

    print("\nAll charts generated successfully!")
