from app6.agents.base_agent import BaseAgent
from app6.llm.llm import LLMService


class AnswerAgent(BaseAgent):
    """
    Specialized agent responsible for generating
    the final natural-language response.

    It synthesizes information produced by:
    - Retrieval Agent
    - SQL Agent
    - Action Agent
    """

    def __init__(self):

        super().__init__(
            name="Answer Agent",
            description=(
                "Generates the final response "
                "using retrieved context and tool results."
            ),
            version="1.0",
        )

        self.llm = LLMService()

    # =========================================================
    # GENERATE FINAL RESPONSE
    # =========================================================

    def execute(self, state):

        query = state.get(
            "query",
            "",
        )

        if not query.strip():

            raise ValueError("Query cannot be empty.")

        intent = state.get(
            "intent",
            "retrieval",
        )

        if hasattr(
            intent,
            "value",
        ):

            intent = intent.value

        intent = str(intent).lower().strip()

        # -----------------------------------------------------
        # Retrieval context
        # -----------------------------------------------------

        retrieval_response = state.get(
            "retrieval_response",
            {},
        )

        if not isinstance(
            retrieval_response,
            dict,
        ):

            retrieval_response = {}

        context = retrieval_response.get(
            "context",
            "",
        )

        # -----------------------------------------------------
        # SQL result
        # -----------------------------------------------------

        sql_result = state.get(
            "sql_result",
            "",
        )

        sql_error = state.get(
            "sql_error",
            "",
        )

        # -----------------------------------------------------
        # Action result
        # -----------------------------------------------------

        action_result = state.get(
            "action_result",
            "",
        )

        action_error = state.get(
            "action_error",
            "",
        )

        # -----------------------------------------------------
        # Combine tool results
        # -----------------------------------------------------

        tool_results = []

        if sql_result:

            tool_results.append(f"SQL Result:\n{sql_result}")

        if sql_error:

            tool_results.append(f"SQL Error:\n{sql_error}")

        if action_result:

            tool_results.append(f"Action Result:\n{action_result}")

        if action_error:

            tool_results.append(f"Action Error:\n{action_error}")

        tool_result = "\n\n".join(tool_results)

        # -----------------------------------------------------
        # Debug
        # -----------------------------------------------------

        print("\n" + "=" * 80)
        print("ANSWER AGENT")
        print("=" * 80)

        print(f"Intent : {intent}")

        print(f"Context Available : " f"{bool(context)}")

        print(f"Tool Result Available : " f"{bool(tool_result)}")

        # -----------------------------------------------------
        # Generate final response
        # -----------------------------------------------------

        try:

            answer = self.llm.generate_answer(
                query=query,
                intent=intent,
                context=context,
                tool_result=tool_result,
            )

        except Exception as e:

            answer = "I was unable to generate " f"a final response: {e}"

        print("\nFinal Answer:")
        print(answer)

        print("=" * 80)

        current_step = state.get(
            "current_step",
            "generate_response",
        )

        return {
            "answer": answer,
            "steps_executed": (
                state.get(
                    "steps_executed",
                    [],
                )
                + [current_step]
            ),
        }
