"""
Document Retrieval Tool

Provides a clean tool interface between the
RetrievalAgent and the underlying RetrievalService.

The tool is intentionally independent of a specific
document type such as PDF, CSV, JSON, etc.
"""

from typing import Any, Dict

from app6.retrieval.retrieval_service import RetrievalService


class RetrievalTool:
    """
    Tool responsible for document retrieval.

    The agent decides WHEN retrieval is required.
    This tool decides HOW to perform the retrieval.
    """

    name = "document_retrieval"

    description = (
        "Searches the document knowledge base " "and returns relevant document context."
    )

    def __init__(self):

        self.retrieval_service = RetrievalService()

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query: str,
    ) -> Dict[str, Any]:
        """
        Search the document knowledge base.

        Parameters
        ----------
        query:
            Natural-language user query.

        Returns
        -------
        Dict[str, Any]
            Retrieval response containing the
            retrieved context and metadata.
        """

        if not query or not query.strip():

            raise ValueError("Retrieval query cannot be empty.")

        result = self.retrieval_service.retrieve(query.strip())

        if result is None:

            return {
                "context": "",
                "results": [],
                "count": 0,
            }

        # -------------------------------------------------
        # Normalize response
        # -------------------------------------------------

        if isinstance(
            result,
            dict,
        ):

            return result

        # -------------------------------------------------
        # Backward compatibility
        # -------------------------------------------------

        if isinstance(
            result,
            list,
        ):

            return {
                "context": "\n\n".join(str(item) for item in result),
                "results": result,
                "count": len(result),
            }

        return {
            "context": str(result),
            "results": [],
            "count": 1,
        }
