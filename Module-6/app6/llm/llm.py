from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app6.config.settings import (
    GROQ_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
)

from app6.models.intent import IntentResult
from app6.models.plan import PlanResult

from app6.prompts.intent_prompt import (
    INTENT_CLASSIFIER_PROMPT,
)

from app6.prompts.planner_prompt import (
    PLANNER_PROMPT,
)


class LLMService:

    def __init__(self):

        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=MODEL_NAME,
            temperature=TEMPERATURE,
        )

    # =========================================================
    # INTENT CLASSIFICATION
    # =========================================================

    def classify_intent(
        self,
        query: str,
    ):

        if not query or not query.strip():

            raise ValueError("Query cannot be empty.")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    INTENT_CLASSIFIER_PROMPT,
                ),
                (
                    "human",
                    "{query}",
                ),
            ]
        )

        parser = JsonOutputParser()

        chain = prompt | self.llm | parser

        try:

            response = chain.invoke(
                {
                    "query": query.strip(),
                }
            )

        except Exception as e:

            raise RuntimeError(f"Intent Classification Failed: {e}")

        # -----------------------------------------------------
        # Debug
        # -----------------------------------------------------

        print("\n" + "=" * 60)
        print("RAW INTENT RESPONSE")
        print("=" * 60)

        for key, value in response.items():

            print(f"{key:<12}: {value}")

        print("=" * 60)

        # -----------------------------------------------------
        # Validate intent
        # -----------------------------------------------------

        VALID_INTENTS = {
            "retrieval",
            "summary",
            "compare",
            "sql",
            "action",
            "greeting",
        }

        intent = (
            str(
                response.get(
                    "Intent",
                    "",
                )
            )
            .lower()
            .strip()
        )

        if intent not in VALID_INTENTS:

            print("\nInvalid Intent Returned by LLM.")

            print("Defaulting to 'retrieval'.")

            intent = "retrieval"

        # -----------------------------------------------------
        # Confidence validation
        # -----------------------------------------------------

        try:

            confidence = float(
                response.get(
                    "Confidence",
                    0.0,
                )
            )

        except (TypeError, ValueError):

            confidence = 0.0

        confidence = max(
            0.0,
            min(
                confidence,
                1.0,
            ),
        )

        return IntentResult(
            intent=intent,
            confidence=confidence,
            reason=response.get(
                "Reason",
                "No reason provided.",
            ),
        )

    # =========================================================
    # PLANNER
    # =========================================================

    def create_plan(
        self,
        query: str,
        intent: str,
    ):
        """
        Generate a structured execution plan
        using the Groq LLM.
        """

        if not query or not query.strip():

            raise ValueError("Query cannot be empty.")

        if not intent or not str(intent).strip():

            raise ValueError("Intent cannot be empty.")

        # -----------------------------------------------------
        # Normalize intent
        # -----------------------------------------------------

        if hasattr(intent, "value"):

            intent = intent.value

        intent = str(intent).lower().strip()

        # -----------------------------------------------------
        # Planner prompt
        # -----------------------------------------------------

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    PLANNER_PROMPT,
                ),
            ]
        )

        parser = JsonOutputParser()

        chain = prompt | self.llm | parser

        try:

            response = chain.invoke(
                {
                    "query": query.strip(),
                    "intent": intent,
                }
            )

        except Exception as e:

            raise RuntimeError(f"Planning Failed: {e}")

        # -----------------------------------------------------
        # Debug
        # -----------------------------------------------------

        print("\n" + "=" * 60)
        print("RAW PLANNER RESPONSE")
        print("=" * 60)

        for key, value in response.items():

            print(f"{key:<12}: {value}")

        print("=" * 60)

        # -----------------------------------------------------
        # Validate planner response
        # -----------------------------------------------------

        try:

            plan_result = PlanResult(
                steps=response.get(
                    "steps",
                    [],
                ),
                reason=response.get(
                    "reason",
                    "No planning reason provided.",
                ),
            )

        except Exception as e:

            raise RuntimeError(f"Invalid Planner Response: {e}")

        return plan_result

    # =========================================================
    # FINAL RESPONSE GENERATION
    # =========================================================

    def generate_answer(
        self,
        query: str,
        context: str = "",
        intent: str = "retrieval",
        tool_result: str = "",
    ):
        """
        Generate the final user-facing answer.

        The answer can be generated from:

        - retrieved document context
        - SQL results
        - action results
        - greeting intent
        """

        if not query or not query.strip():

            raise ValueError("Query cannot be empty.")

        # -----------------------------------------------------
        # Normalize intent
        # -----------------------------------------------------

        if hasattr(intent, "value"):

            intent = intent.value

        intent = str(intent).lower().strip()

        # -----------------------------------------------------
        # Final response prompt
        # -----------------------------------------------------

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are the final response agent in a production
Agentic AI system.

Your job is to answer the user's query using the
available information provided below.

Detected Intent:
{intent}

Rules:

1. Answer the user's actual question directly.

2. Use the provided context when it is available.

3. Use the tool result when it is available.

4. Do not invent facts.

5. If the available information is insufficient,
   clearly say that there is not enough information
   to answer reliably.

6. For greeting:
   respond naturally and briefly.

7. For retrieval:
   explain the requested information using the
   retrieved document context.

8. For summary:
   provide a concise summary based on the
   retrieved document context.

9. For comparison:
   clearly compare the requested information
   based on the available context.

10. For SQL:
    explain the SQL result clearly.

11. For action:
    clearly explain the action result or
    approval requirement.

12. Do not mention:
    - internal agents
    - planning
    - LangGraph
    - prompts
    - tools
    - implementation details
    - model names

13. Return only the final answer to the user.
                    """,
                ),
                (
                    "human",
                    """
User Query:
{query}

Retrieved Context:
{context}

Tool Result:
{tool_result}
                    """,
                ),
            ]
        )

        chain = prompt | self.llm

        try:

            response = chain.invoke(
                {
                    "query": query.strip(),
                    "context": context or "",
                    "intent": intent,
                    "tool_result": tool_result or "",
                }
            )

        except Exception as e:

            raise RuntimeError(f"Answer Generation Failed: {e}")

        # -----------------------------------------------------
        # Extract response
        # -----------------------------------------------------

        answer = response.content

        if isinstance(answer, list):

            answer = "".join(str(item) for item in answer)

        if not answer:

            raise RuntimeError("LLM returned an empty response.")

        return str(answer).strip()
