from app6.llm.llm import LLMService
from app6.models.agent_state import AgentState
from app6.models.plan import PlanStep


class Planner:

    MAX_STEPS = 5

    ALLOWED_STEPS = {step.value for step in PlanStep}

    def __init__(self):

        self.llm = LLMService()

    def create_plan(
        self,
        state: AgentState,
    ):

        query = state["query"]

        intent = state.get(
            "intent",
            "retrieval",
        )

        print("\n" + "=" * 80)
        print("PLANNER")
        print("=" * 80)

        print(f"Query  : {query}")
        print(f"Intent : {intent}")

        # -------------------------------------------------
        # Ask LLM to create plan
        # -------------------------------------------------

        intent = state.get("intent")

        if hasattr(intent, "value"):
            intent = intent.value

        plan_result = self.llm.create_plan(
            query=query,
            intent=intent,
        )

        steps = plan_result.steps

        # -------------------------------------------------
        # Validate empty plan
        # -------------------------------------------------

        if not steps:

            raise RuntimeError("Planner returned an empty plan.")

        # -------------------------------------------------
        # Validate maximum steps
        # -------------------------------------------------

        if len(steps) > self.MAX_STEPS:

            raise RuntimeError("Planner returned more than " f"{self.MAX_STEPS} steps.")

        # -------------------------------------------------
        # Convert Enum → string
        # -------------------------------------------------

        step_values = [step.value for step in steps]

        # -------------------------------------------------
        # Validate allowed steps
        # -------------------------------------------------

        invalid_steps = [step for step in step_values if step not in self.ALLOWED_STEPS]

        if invalid_steps:

            raise RuntimeError("Planner returned invalid steps: " f"{invalid_steps}")

        # -------------------------------------------------
        # Print execution plan
        # -------------------------------------------------

        print("\nExecution Plan:")

        for index, step in enumerate(
            step_values,
            start=1,
        ):

            print(f"{index}. {step}")

        print(f"\nReason: " f"{plan_result.reason}")

        # -------------------------------------------------
        # Return plain strings
        # -------------------------------------------------

        return {
            "plan": step_values,
            "plan_reason": plan_result.reason,
        }
