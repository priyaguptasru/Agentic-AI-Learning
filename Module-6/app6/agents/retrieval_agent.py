"""
Retrieval Agent

The RetrievalAgent is responsible for deciding that
document retrieval is required and invoking the
document retrieval tool.
"""

from app6.agents.base_agent import BaseAgent
from app6.tools.retrieval_tool import RetrievalTool


class RetrievalAgent(BaseAgent):
    """
    Specialized agent for document retrieval.

    Agent responsibility:
        Decide/use the retrieval capability.

    Tool responsibility:
        Actually perform the document search.
    """

    def __init__(self):

        super().__init__(
            name="Retrieval Agent",
            description=(
                "Retrieves relevant information " "from the document knowledge base."
            ),
            version="1.0",
        )

        self.tool = RetrievalTool()

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        state,
    ):
        """
        Execute document retrieval.
        """

        query = state.get(
            "query",
            "",
        )

        if not query or not query.strip():

            raise ValueError("Retrieval query cannot be empty.")

        print("\nRetrievalAgent")
        print("=" * 80)
        print(f"Query : {query}")

        try:

            retrieval_response = self.tool.search(query)

        except Exception as e:

            print(f"\nRetrieval Tool Error: {e}")

            return {
                "retrieval_error": str(e),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["retrieve_documents_failed"]
                ),
            }

        # -------------------------------------------------
        # Normalize response
        # -------------------------------------------------

        if not isinstance(
            retrieval_response,
            dict,
        ):

            retrieval_response = {
                "context": str(retrieval_response),
                "results": [],
                "count": 1,
            }

        context = retrieval_response.get(
            "context",
            "",
        )

        print(f"Retrieval response type : " f"{type(retrieval_response).__name__}")

        print(f"Context Available : " f"{bool(context)}")

        print(f"Context Length : " f"{len(str(context))}")

        return {
            "retrieval_response": (retrieval_response),
            "steps_executed": (
                state.get(
                    "steps_executed",
                    [],
                )
                + ["retrieve_documents"]
            ),
        }
