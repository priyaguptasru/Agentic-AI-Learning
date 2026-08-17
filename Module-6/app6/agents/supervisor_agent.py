from typing import Any, Dict

from app6.agents.retrieval_agent import RetrievalAgent
from app6.agents.sql_agent import SQLAgent
from app6.agents.action_agent import ActionAgent
from app6.agents.answer_agent import AnswerAgent


class SupervisorAgent:
    """
    Supervisor Agent

    Responsible for coordinating specialized agents.

    The Supervisor does NOT create the plan.
    The Planner creates the plan.

    The Supervisor:
        1. Reads the current execution step.
        2. Selects the appropriate specialized agent.
        3. Executes that agent.
        4. Returns the updated state.
    """

    def __init__(self):

        print("\nInitializing Supervisor Agent...")

        # -------------------------------------------------
        # Initialize specialized agents
        # -------------------------------------------------

        self.retrieval_agent = RetrievalAgent()

        self.sql_agent = SQLAgent()

        self.action_agent = ActionAgent()

        self.answer_agent = AnswerAgent()

        # -------------------------------------------------
        # Agent registry
        # -------------------------------------------------

        self.agent_registry = {
            "retrieve_documents": self.retrieval_agent,
            "execute_sql": self.sql_agent,
            "validate_action": self.action_agent,
            "execute_action": self.action_agent,
            "generate_response": self.answer_agent,
        }

        print("Supervisor Agent Ready!")

    # =====================================================
    # GET AGENT
    # =====================================================

    def get_agent(self, step: str):

        if not step:

            raise ValueError("Supervisor received an empty execution step.")

        agent = self.agent_registry.get(step)

        if agent is None:

            raise ValueError(f"Supervisor does not have an agent " f"for step: {step}")

        return agent

    # =====================================================
    # EXECUTE CURRENT STEP
    # =====================================================

    def execute(self, state: Dict[str, Any]):

        current_step = state.get("current_step")

        if not current_step:

            raise ValueError(
                "Supervisor cannot execute because " "current_step is missing."
            )

        print("\n" + "=" * 80)
        print("SUPERVISOR AGENT")
        print("=" * 80)

        print(f"Current Step : {current_step}")

        # -------------------------------------------------
        # Select specialized agent
        # -------------------------------------------------

        agent = self.get_agent(current_step)

        print(f"Selected Agent : " f"{agent.__class__.__name__}")

        print(f"Executing {agent.__class__.__name__}...")

        # -------------------------------------------------
        # Execute specialized agent
        # -------------------------------------------------

        result = self._execute_agent(
            agent,
            current_step,
            state,
        )

        print(f"Completed : {current_step}")

        print("=" * 80)

        return result

    # =====================================================
    # AGENT EXECUTION
    # =====================================================

    def _execute_agent(
        self,
        agent,
        step: str,
        state: Dict[str, Any],
    ):

        # -------------------------------------------------
        # Action Agent has two different operations
        # -------------------------------------------------

        if step == "validate_action":

            return agent.validate(state)

        if step == "execute_action":

            return agent.execute(state)

        # -------------------------------------------------
        # All other agents use execute()
        # -------------------------------------------------

        return agent.execute(state)

    # =====================================================
    # CHECK NEXT STEP
    # =====================================================

    def get_next_step(self, state):

        plan = state.get(
            "plan",
            [],
        )

        current_step = state.get("current_step")

        if not plan:

            return None

        try:

            current_index = plan.index(current_step)

        except ValueError:

            return None

        next_index = current_index + 1

        if next_index >= len(plan):

            return None

        return plan[next_index]
