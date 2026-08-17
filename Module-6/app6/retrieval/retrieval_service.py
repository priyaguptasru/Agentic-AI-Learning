import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()

# Module-6
MODULE6_ROOT = CURRENT_FILE.parents[2]

# Agentic AI
PROJECT_ROOT = MODULE6_ROOT.parent

# Module-4
MODULE4_ROOT = PROJECT_ROOT / "Module-4"

if str(MODULE4_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE4_ROOT))

from app.services.hybrid_search import HybridSearchService


class RetrievalService:

    def __init__(self):

        self.hybrid_search = HybridSearchService()

    def retrieve(self, query: str):

        results = self.hybrid_search.search(query)

        cleaned_results = []

        context_parts = []

        for result in results:

            cleaned_result = {
                "document": result["document"],
                "page": result["page"],
                "section": result["section"],
                "text": result["text"],
                "score": result["final_score"],
                "similarity": result["similarity"],
                "source": result["source"],
            }

            cleaned_results.append(cleaned_result)

            context_parts.append(f"""
    Document : {result['document']}
    Page     : {result['page']}
    Section  : {result['section']}

    {result['text']}
    """)

        context = "\n" + ("-" * 80 + "\n").join(context_parts)

        return {
            "chunks": cleaned_results,
            "context": context,
        }
