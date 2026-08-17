"""
Agent Workflow
==============

Main LangGraph workflow for Module-6.

Responsibilities
----------------

1. Classify user intent.
2. Generate an execution plan.
3. Execute planned steps sequentially.
4. Route execution deterministically.
5. Enforce execution limits.
6. Detect agent failures.
7. Retry explicitly retryable failures.
8. Detect missing information.
9. Handle low-confidence situations.
10. Support human-in-the-loop approval.
11. Pause execution for approval.
12. Resume execution after approval.
13. Safely exit when approval is rejected.
14. Maintain traceable execution steps.

Architecture
------------

User
  |
  v
Intent Classification
  |
  +---- failure ----> SAFE EXIT
  |
  v
Planning
  |
  v
Initialize Execution
  |
  v
Execution Control
  |
  v
Supervisor
  |
  v
Agent Result Check
  |
  v
Deterministic Workflow Router
  |
  +--> CONTINUE
  |
  +--> RETRY
  |
  +--> ASK_USER
  |
  +--> REQUIRE_APPROVAL
  |
  +--> SAFE_EXIT
  |
  +--> COMPLETE
"""

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from time import sleep
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from langgraph.types import (
    interrupt,
    Command,
)

from app6.models.agent_state import AgentState

from app6.intent.intent_classifier import (
    IntentClassifier,
)

from app6.planners.planner import Planner

from app6.agents.supervisor_agent import (
    SupervisorAgent,
)

from app6.routing.workflow_router import (
    WorkflowRouter,
)


class AgentWorkflow:
    """
    Main LangGraph workflow.

    LLM-driven decisions:

        - Intent classification
        - Plan generation
        - Natural-language interpretation

    Deterministic decisions:

        - Step validation
        - Agent routing
        - Execution limits
        - Retry handling
        - Missing-information routing
        - Confidence routing
        - Approval checks
        - Stop conditions
        - Plan completion
    """

    # =====================================================
    # CONFIGURATION
    # =====================================================

    MAX_EXECUTION_STEPS = 10

    MAX_RETRIES = 2

    # Maximum time allowed for a single supervisor/agent execution.
    # This is intentionally generic and applies to all agent steps.
    # Timeout failures are only retried for safe/read-oriented steps.
    AGENT_TIMEOUT_SECONDS = 30

    # Retry backoff configuration.
    RETRY_BASE_DELAY_SECONDS = 1.0
    RETRY_MAX_DELAY_SECONDS = 8.0

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        print("\nInitializing Agent Workflow...")

        # -------------------------------------------------
        # LLM-driven components
        # -------------------------------------------------

        self.intent_classifier = IntentClassifier()

        self.planner = Planner()

        # -------------------------------------------------
        # Supervisor
        # -------------------------------------------------

        self.supervisor = SupervisorAgent()

        # -------------------------------------------------
        # Deterministic workflow router
        # -------------------------------------------------

        self.workflow_router = WorkflowRouter(
            low_confidence_threshold=0.70,
            max_retries=self.MAX_RETRIES,
        )

        # -------------------------------------------------
        # Build LangGraph
        # -------------------------------------------------

        self.graph = self._build_graph()

        print("Agent Workflow Ready!")

    # =====================================================
    # NODE 1
    # INTENT CLASSIFICATION
    # =====================================================

    def classify_intent(
        self,
        state: AgentState,
    ):

        print("\n" + "=" * 80)
        print("NODE: INTENT CLASSIFIER")
        print("=" * 80)

        query = state.get(
            "query",
            "",
        )

        if not query.strip():

            return {
                "execution_status": "failed",
                "stop_reason": "Query cannot be empty.",
                "error": "Query cannot be empty.",
            }

        try:

            result = self.intent_classifier.classify(query)

        except Exception as e:

            print(f"\nIntent classification failed: {e}")

            return {
                "intent": None,
                "confidence": 0.0,
                "intent_reason": "",
                "execution_status": "failed",
                "stop_reason": ("Intent classification failed."),
                "error": str(e),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["intent_classification_failed"]
                ),
            }

        print(f"\nIntent     : {result.intent}")

        print(f"Confidence : {result.confidence}")

        print(f"Reason     : {result.reason}")

        # -------------------------------------------------
        # Normalize intent before storing it in workflow state
        # -------------------------------------------------
        # LangGraph checkpoints should contain simple serializable
        # values rather than custom Enum objects.
        if hasattr(result.intent, "value"):

            normalized_intent = result.intent.value

        else:

            normalized_intent = str(result.intent).lower().strip()

        return {
            "intent": normalized_intent,
            "confidence": result.confidence,
            "intent_reason": result.reason,
            "execution_status": "running",
            "steps_executed": (
                state.get(
                    "steps_executed",
                    [],
                )
                + ["intent_classification"]
            ),
        }

    # =====================================================
    # ROUTER AFTER INTENT CLASSIFICATION
    # =====================================================

    def route_after_intent_classification(
        self,
        state: AgentState,
    ):
        """
        Deterministically decide whether planning
        can continue after intent classification.

        IMPORTANT:

        Planning must never execute if intent
        classification has failed.
        """

        execution_status = state.get(
            "execution_status",
            "running",
        )

        intent = state.get("intent")

        # -------------------------------------------------
        # Intent classification failed
        # -------------------------------------------------

        if execution_status == "failed":

            print("\n" + "=" * 80)
            print("INTENT CLASSIFICATION FAILED")
            print("=" * 80)

            print("Workflow will stop before planning.")

            return "stop"

        # -------------------------------------------------
        # No intent
        # -------------------------------------------------

        if not intent:

            print("\n" + "=" * 80)
            print("NO VALID INTENT")
            print("=" * 80)

            print("Workflow will stop before planning.")

            return "stop"

        # -------------------------------------------------
        # Low confidence
        # -------------------------------------------------

        if self.workflow_router.low_confidence(state):

            print("\n" + "=" * 80)
            print("LOW INTENT CONFIDENCE")
            print("=" * 80)

            print(f"Confidence : " f"{state.get('confidence', 0.0)}")

            print(f"Threshold  : " f"{self.workflow_router.low_confidence_threshold}")

            # We allow the workflow to continue here
            # because the planner may still be able to
            # produce a useful plan.

            # If the planner/agent later requires
            # clarification, the deterministic router
            # can send the workflow to ASK_USER.

        return "continue"

    # =====================================================
    # NODE 2
    # PLANNING
    # =====================================================

    def create_plan(
        self,
        state: AgentState,
    ):

        print("\n" + "=" * 80)
        print("PLANNER")
        print("=" * 80)

        query = state.get(
            "query",
            "",
        )

        intent = state.get("intent")

        if not intent:

            return {
                "execution_status": "failed",
                "stop_reason": ("Planning cannot start " "without a valid intent."),
                "error": ("Planning cannot start " "without a valid intent."),
            }

        try:

            plan_result = self.planner.create_plan(state)

        except Exception as e:

            print(f"\nPlanning failed: {e}")

            return {
                "execution_status": "failed",
                "stop_reason": "Planning failed.",
                "error": str(e),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["planning_failed"]
                ),
            }

        # -------------------------------------------------
        # Support PlanResult-style response
        # -------------------------------------------------

        if hasattr(
            plan_result,
            "steps",
        ):

            plan = plan_result.steps

            plan_reason = getattr(
                plan_result,
                "reason",
                "No planning reason provided.",
            )

        else:

            plan = plan_result.get(
                "plan",
                plan_result.get(
                    "steps",
                    [],
                ),
            )

            plan_reason = plan_result.get(
                "plan_reason",
                plan_result.get(
                    "reason",
                    "No planning reason provided.",
                ),
            )

        if not plan:

            return {
                "execution_status": "failed",
                "stop_reason": ("Planner returned an empty plan."),
                "error": ("Planner returned an empty plan."),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["planning_failed"]
                ),
            }

        print("\nExecution Plan:")

        for index, step in enumerate(
            plan,
            start=1,
        ):

            if hasattr(
                step,
                "value",
            ):

                step_name = step.value

            else:

                step_name = str(step)

            print(f"{index}. {step_name}")

        print(f"\nReason: {plan_reason}")

        return {
            "plan": plan,
            "plan_reason": plan_reason,
            "execution_status": "running",
            "steps_executed": (
                state.get(
                    "steps_executed",
                    [],
                )
                + ["planning"]
            ),
        }

    # =====================================================
    # NODE 3
    # INITIALIZE EXECUTION
    # =====================================================

    def initialize_execution(
        self,
        state: AgentState,
    ):

        plan = state.get(
            "plan",
            [],
        )

        if not plan:

            return {
                "execution_status": "failed",
                "stop_reason": ("Execution cannot start " "because the plan is empty."),
                "error": ("Execution plan is empty."),
            }

        first_step = plan[0]

        if hasattr(
            first_step,
            "value",
        ):

            first_step = first_step.value

        print("\n" + "=" * 80)
        print("INITIALIZE EXECUTION")
        print("=" * 80)

        print(f"First Step : {first_step}")

        return {
            "current_step": first_step,
            "next_step": None,
            "execution_count": 0,
            "retry_count": 0,
            "execution_status": "running",
            "stop_reason": "",
            "retryable_failure": False,
            "missing_information": "",
            "needs_user_input": False,
            "user_input_required": False,
            "confidence_clarification_completed": False,
        }

    # =====================================================
    # NODE 4
    # EXECUTION CONTROL
    # =====================================================

    def check_execution_limit(
        self,
        state: AgentState,
    ):

        current_step = state.get("current_step")

        execution_count = state.get(
            "execution_count",
            0,
        )

        status = state.get(
            "execution_status",
            "running",
        )

        # -------------------------------------------------
        # Existing terminal state
        # -------------------------------------------------

        if status in {
            "failed",
            "stopped",
            "completed",
        }:

            return {
                "execution_status": status,
            }

        # -------------------------------------------------
        # Current step must exist
        # -------------------------------------------------

        if not current_step:

            return {
                "execution_status": "failed",
                "stop_reason": ("No current execution " "step was available."),
                "error": ("No current execution " "step was available."),
            }

        # -------------------------------------------------
        # Validate step
        # -------------------------------------------------

        if not self.workflow_router.is_valid_step(current_step):

            return {
                "execution_status": "failed",
                "stop_reason": (f"Invalid execution step: " f"{current_step}"),
                "error": (f"Invalid execution step: " f"{current_step}"),
            }

        # -------------------------------------------------
        # Execution limit
        # -------------------------------------------------

        if self.workflow_router.execution_limit_reached(
            execution_count,
            self.MAX_EXECUTION_STEPS,
        ):

            print("\n" + "=" * 80)
            print("EXECUTION LIMIT REACHED")
            print("=" * 80)

            print(f"Execution Count : " f"{execution_count}")

            print(f"Maximum Allowed : " f"{self.MAX_EXECUTION_STEPS}")

            return {
                "execution_status": "stopped",
                "stop_reason": ("Maximum execution steps reached."),
            }

        # -------------------------------------------------
        # Increment execution count
        # -------------------------------------------------

        new_count = execution_count + 1

        print("\n" + "=" * 80)
        print("EXECUTION CONTROL")
        print("=" * 80)

        print(f"Current Step     : " f"{current_step}")

        print(f"Execution Count  : " f"{new_count}/" f"{self.MAX_EXECUTION_STEPS}")

        return {
            "execution_count": new_count,
            "execution_status": "running",
        }

    # =====================================================
    # ROUTER AFTER EXECUTION LIMIT
    # =====================================================

    def route_after_execution_limit(
        self,
        state: AgentState,
    ):

        status = state.get(
            "execution_status",
            "running",
        )

        if status in {
            "failed",
            "stopped",
            "completed",
        }:

            return "stop"

        return "continue"

    # =====================================================
    # NODE 5
    # SUPERVISOR EXECUTION
    # =====================================================

    def supervisor_execute(
        self,
        state: AgentState,
    ):

        current_step = state.get("current_step")

        print("\n" + "=" * 80)
        print("SUPERVISOR AGENT")
        print("=" * 80)

        print(f"Current Step : " f"{current_step}")

        # -------------------------------------------------
        # Validate step
        # -------------------------------------------------

        if not self.workflow_router.is_valid_step(current_step):

            return {
                "execution_status": "failed",
                "stop_reason": (f"Invalid workflow step: " f"{current_step}"),
                "error": (f"Invalid workflow step: " f"{current_step}"),
            }

        # -------------------------------------------------
        # Greeting
        # -------------------------------------------------

        if current_step == "greeting":

            print("Selected Agent : None")

            print("Handling greeting step...")

            return {
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["greeting"]
                ),
                "execution_status": "running",
            }

        # -------------------------------------------------
        # Deterministic agent selection
        # -------------------------------------------------

        try:

            agent_name = self.workflow_router.get_agent_name(current_step)

        except Exception as e:

            return {
                "execution_status": "failed",
                "stop_reason": ("Deterministic routing failed."),
                "error": str(e),
            }

        print(f"Selected Agent : " f"{agent_name}")

        # -------------------------------------------------
        # Supervisor executes selected agent
        # -------------------------------------------------

        # -------------------------------------------------
        # Execute with a bounded timeout.
        # -------------------------------------------------
        # A timeout is treated as a retryable failure only for
        # read-oriented/transient steps. Business actions are
        # deliberately NOT retried after a timeout because the
        # external operation may have already started.
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.supervisor.execute, state)

        try:

            result = future.result(
                timeout=self.AGENT_TIMEOUT_SECONDS,
            )

        except FutureTimeoutError:

            current_step = state.get(
                "current_step",
                "",
            )

            retryable_steps = {
                "retrieve_documents",
                "execute_sql",
            }

            retryable = current_step in retryable_steps

            print("\n" + "=" * 80)
            print("AGENT EXECUTION TIMEOUT")
            print("=" * 80)
            print(f"Step    : {current_step}")
            print(f"Timeout : {self.AGENT_TIMEOUT_SECONDS} seconds")
            print("Retry   : " + ("allowed" if retryable else "blocked"))
            print("=" * 80)

            future.cancel()
            executor.shutdown(
                wait=False,
                cancel_futures=True,
            )

            return {
                "execution_status": ("running" if retryable else "failed"),
                "stop_reason": (
                    f"Agent execution timed out after "
                    f"{self.AGENT_TIMEOUT_SECONDS} seconds."
                ),
                "error": (
                    f"Agent execution timed out after "
                    f"{self.AGENT_TIMEOUT_SECONDS} seconds."
                ),
                "retryable_failure": retryable,
                "failure_type": "timeout",
            }

        except Exception as e:

            executor.shutdown(
                wait=False,
                cancel_futures=True,
            )

            print("\nSupervisor execution failed:")

            print(e)

            current_step = state.get(
                "current_step",
                "",
            )

            retryable = current_step in {
                "retrieve_documents",
                "execute_sql",
            }

            return {
                "execution_status": ("running" if retryable else "failed"),
                "stop_reason": ("Supervisor execution failed."),
                "error": str(e),
                "retryable_failure": retryable,
                "failure_type": "execution_error",
            }

        else:

            executor.shutdown(
                wait=False,
                cancel_futures=True,
            )

        if result is None:

            current_step = state.get(
                "current_step",
                "",
            )

            retryable = current_step in {
                "retrieve_documents",
                "execute_sql",
            }

            return {
                "execution_status": ("running" if retryable else "failed"),
                "stop_reason": ("Supervisor returned no result."),
                "error": ("Supervisor returned no result."),
                "retryable_failure": retryable,
                "failure_type": "empty_result",
            }

        return result

    # =====================================================
    # NODE 6
    # CHECK AGENT RESULT
    # =====================================================

    def check_agent_result(
        self,
        state: AgentState,
    ):
        """
        Inspect the latest agent result and determine
        whether the failure is retryable.

        Important:

        Not every failure should automatically retry.
        """

        # -------------------------------------------------
        # Missing information
        # -------------------------------------------------

        if state.get("missing_information"):

            return {
                "execution_status": "running",
                "needs_user_input": True,
            }

        if state.get("needs_user_input"):

            return {
                "execution_status": "running",
                "needs_user_input": True,
            }

        # -------------------------------------------------
        # Timeout / failure classification
        # -------------------------------------------------

        if state.get("failure_type") == "timeout":

            current_step = state.get(
                "current_step",
                "",
            )

            retryable = current_step in {
                "retrieve_documents",
                "execute_sql",
            }

            return {
                "execution_status": ("running" if retryable else "failed"),
                "stop_reason": state.get(
                    "error",
                    "Agent execution timed out.",
                ),
                "retryable_failure": retryable,
            }

        # -------------------------------------------------
        # General error
        # -------------------------------------------------

        if state.get("error"):

            current_step = state.get(
                "current_step",
                "",
            )

            retryable = current_step in {
                "retrieve_documents",
                "execute_sql",
            }

            return {
                "execution_status": ("running" if retryable else "failed"),
                "stop_reason": state.get("error"),
                "retryable_failure": retryable,
            }

        # -------------------------------------------------
        # Retrieval error
        # -------------------------------------------------

        if state.get("retrieval_error"):

            return {
                "execution_status": "running",
                "retryable_failure": True,
            }

        # -------------------------------------------------
        # SQL error
        # -------------------------------------------------

        if state.get("sql_error"):

            return {
                "execution_status": "running",
                "retryable_failure": True,
            }

        # -------------------------------------------------
        # Action error
        # -------------------------------------------------

        if state.get("action_error"):

            current_step = state.get(
                "current_step",
                "",
            )

            # Action errors should not blindly retry.
            # The workflow should continue to the final
            # response so the user receives a clear result.

            if current_step in {
                "validate_action",
                "execute_action",
            }:

                print("\nAction issue detected.")

                print("Routing to generate_response.")

                return {
                    "execution_status": "running",
                    "retryable_failure": False,
                }

            return {
                "execution_status": "failed",
                "stop_reason": state.get("action_error"),
                "retryable_failure": False,
            }

        # -------------------------------------------------
        # Successful execution
        # -------------------------------------------------

        return {
            "execution_status": "running",
            "retryable_failure": False,
        }

    # =====================================================
    # ROUTER AFTER AGENT RESULT
    # =====================================================

    def route_after_agent_result(
        self,
        state: AgentState,
    ):

        decision = self.workflow_router.route(state)

        print(f"\nAgent Result Router Decision : " f"{decision}")

        if decision == WorkflowRouter.RETRY:
            return "retry"

        if decision == WorkflowRouter.ASK_USER:
            return "ask_user"

        if decision == WorkflowRouter.REQUIRE_APPROVAL:
            return "human_approval"

        if decision == WorkflowRouter.SAFE_EXIT:
            return "stop"

        if decision == WorkflowRouter.COMPLETE:
            return "stop"

        return "continue"

    # =====================================================
    # NODE 7
    # PREPARE NEXT STEP
    # =====================================================

    def prepare_next_step(
        self,
        state: AgentState,
    ):

        plan = state.get(
            "plan",
            [],
        )

        current_step = state.get("current_step")

        status = state.get(
            "execution_status",
            "running",
        )

        # -------------------------------------------------
        # Terminal state
        # -------------------------------------------------

        if status in {
            "failed",
            "stopped",
            "completed",
        }:

            return {"next_step": None}

        if not plan:

            return {
                "execution_status": "failed",
                "stop_reason": ("Execution plan is empty."),
                "next_step": None,
            }

        if current_step is None:

            return {
                "execution_status": "failed",
                "stop_reason": ("Current execution step " "is missing."),
                "next_step": None,
            }

        # -------------------------------------------------
        # Normalize plan
        # -------------------------------------------------

        normalized_plan = []

        for step in plan:

            if hasattr(
                step,
                "value",
            ):

                normalized_plan.append(step.value)

            else:

                normalized_plan.append(str(step))

        # -------------------------------------------------
        # Find current step
        # -------------------------------------------------

        try:

            current_index = normalized_plan.index(current_step)

        except ValueError:

            return {
                "execution_status": "failed",
                "stop_reason": (
                    f"Current step "
                    f"'{current_step}' "
                    "was not found in "
                    "the execution plan."
                ),
                "next_step": None,
            }

        # -------------------------------------------------
        # Action failure
        # -------------------------------------------------

        if state.get("action_error"):

            if current_step in {
                "validate_action",
                "execute_action",
            }:

                if "generate_response" in normalized_plan:

                    print("\nAction failed safely.")

                    print("Routing to " "generate_response.")

                    return {
                        "next_step": ("generate_response"),
                        "execution_status": "running",
                        "retryable_failure": False,
                    }

        # -------------------------------------------------
        # Next step
        # -------------------------------------------------

        next_index = current_index + 1

        # -------------------------------------------------
        # Plan completed
        # -------------------------------------------------

        if next_index >= len(normalized_plan):

            print("\n" + "=" * 80)
            print("PLAN COMPLETED")
            print("=" * 80)

            print("All planned steps " "were executed successfully.")

            return {
                "next_step": None,
                "execution_status": "completed",
                "stop_reason": ("All planned steps completed."),
            }

        next_step = normalized_plan[next_index]

        # -------------------------------------------------
        # Validate next step
        # -------------------------------------------------

        if not self.workflow_router.is_valid_step(next_step):

            return {
                "execution_status": "failed",
                "stop_reason": (f"Invalid next workflow " f"step: {next_step}"),
                "error": (f"Invalid next workflow " f"step: {next_step}"),
                "next_step": None,
            }

        print(f"\nNext Step : " f"{next_step}")

        return {
            "next_step": next_step,
            "retry_count": 0,
            "retryable_failure": False,
            "failure_type": "",
        }

    # =====================================================
    # ROUTER AFTER NEXT STEP
    # =====================================================

    def route_after_next_step(
        self,
        state: AgentState,
    ):

        status = state.get(
            "execution_status",
            "running",
        )

        if status in {
            "failed",
            "stopped",
            "completed",
        }:

            return "stop"

        next_step = state.get("next_step")

        if next_step is None:

            return "stop"

        # -------------------------------------------------
        # Approval gate
        # -------------------------------------------------

        if self.workflow_router.approval_pending(state):

            return "human_approval"

        return "continue"

    # =====================================================
    # NODE 8
    # RETRY
    # =====================================================

    def retry_execution(
        self,
        state: AgentState,
    ):
        """
        Prepare the current step for another attempt.
        """

        retry_count = self.workflow_router.retry_count(state)

        if not self.workflow_router.retry_available(state):

            return {
                "execution_status": "stopped",
                "stop_reason": ("Maximum retry attempts reached."),
                "retryable_failure": False,
            }

        new_retry_count = retry_count + 1

        current_step = state.get(
            "current_step",
            "",
        )

        # Exponential backoff prevents rapid repeated calls to
        # an unhealthy dependency. Example with base=1s:
        # retry 1 -> 1s, retry 2 -> 2s, retry 3 -> 4s.
        delay = min(
            self.RETRY_BASE_DELAY_SECONDS * (2 ** (new_retry_count - 1)),
            self.RETRY_MAX_DELAY_SECONDS,
        )

        print("\n" + "=" * 80)
        print("WORKFLOW RETRY")
        print("=" * 80)

        print(f"Step   : {current_step}")
        print(f"Retry  : {new_retry_count}/{self.MAX_RETRIES}")
        print(f"Backoff: {delay:.1f} seconds")

        sleep(delay)

        return {
            "retry_count": new_retry_count,
            "execution_status": "running",
            "retryable_failure": False,
            "stop_reason": "",
            "failure_type": "",
        }

    # =====================================================
    # NODE 9
    # REQUEST USER INFORMATION
    # =====================================================

    def request_user_information(
        self,
        state: AgentState,
    ):
        """
        Pause workflow execution and request
        additional information from the user.
        """

        missing = state.get(
            "missing_information",
            "Additional information is required.",
        )

        if isinstance(
            missing,
            (list, tuple),
        ):

            missing_text = ", ".join(str(item) for item in missing)

        else:

            missing_text = str(missing)

        print("\n" + "=" * 80)
        print("USER INFORMATION REQUIRED")
        print("=" * 80)

        print(f"Required Information : " f"{missing_text}")

        response = interrupt(
            {
                "type": "user_input",
                "message": (
                    "Additional information "
                    "is required before "
                    "the workflow can continue."
                ),
                "missing_information": (missing_text),
                "query": state.get(
                    "query",
                    "",
                ),
            }
        )

        user_input = str(response).strip()

        if not user_input:

            return {
                "execution_status": "stopped",
                "stop_reason": ("Required user information " "was not provided."),
                "needs_user_input": False,
            }

        original_query = state.get(
            "query",
            "",
        )

        enriched_query = (
            f"{original_query}\n\n" f"Additional user information:\n" f"{user_input}"
        )

        return {
            "query": enriched_query,
            "user_input": user_input,
            "missing_information": "",
            "needs_user_input": False,
            "user_input_required": False,
            "confidence_clarification_completed": True,
            "execution_status": "running",
            "retryable_failure": False,
            "steps_executed": (
                state.get(
                    "steps_executed",
                    [],
                )
                + ["user_clarification"]
            ),
        }

    # =====================================================
    # ROUTER AFTER USER INFORMATION
    # =====================================================

    def route_after_user_information(
        self,
        state: AgentState,
    ):

        if state.get("execution_status") in {
            "failed",
            "stopped",
            "completed",
        }:

            return "stop"

        return "continue"

    # =====================================================
    # NODE 10
    # HUMAN APPROVAL
    # =====================================================

    def human_approval(
        self,
        state: AgentState,
    ):
        """
        Pause workflow and request human approval.
        """

        action = state.get(
            "action",
            {},
        )

        approval_request = state.get(
            "approval_request",
            {},
        )

        action_name = (
            action.get(
                "action",
                "unknown",
            )
            if isinstance(
                action,
                dict,
            )
            else "unknown"
        )

        reason = approval_request.get(
            "reason",
            state.get(
                "approval_reason",
                "Approval required.",
            ),
        )

        confidence = approval_request.get(
            "confidence",
            state.get(
                "confidence",
                0.0,
            ),
        )

        threshold = approval_request.get(
            "threshold",
            0.80,
        )

        print("\n" + "=" * 80)
        print("HUMAN APPROVAL REQUIRED")
        print("=" * 80)

        print(f"Action             : " f"{action_name}")

        print(f"Reason             : " f"{reason}")

        print(f"Confidence         : " f"{confidence}")

        print(f"Approval Threshold : " f"{threshold}")

        print("=" * 80)

        decision = interrupt(
            {
                "type": "human_approval",
                "message": (
                    "Human approval is required " "before this action can continue."
                ),
                "action": action,
                "reason": reason,
                "confidence": confidence,
                "threshold": threshold,
            }
        )

        # -------------------------------------------------
        # Normalize decision
        # -------------------------------------------------

        if isinstance(
            decision,
            dict,
        ):

            if decision.get("approved") is True:

                normalized = "approved"

            elif decision.get("approved") is False:

                normalized = "rejected"

            else:

                normalized = (
                    str(
                        decision.get(
                            "decision",
                            "",
                        )
                    )
                    .strip()
                    .lower()
                )

        else:

            normalized = str(decision).strip().lower()

        # -------------------------------------------------
        # APPROVED
        # -------------------------------------------------

        if normalized in {
            "approve",
            "approved",
            "yes",
            "y",
            "true",
        }:

            print("\n" + "=" * 80)
            print("HUMAN APPROVAL: APPROVED")
            print("=" * 80)

            return {
                "approval_status": "approved",
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["human_approval_approved"]
                ),
            }

        # -------------------------------------------------
        # REJECTED
        # -------------------------------------------------

        print("\n" + "=" * 80)
        print("HUMAN APPROVAL: REJECTED")
        print("=" * 80)

        return {
            "approval_status": "rejected",
            "action_result": (
                f"Action '{action_name}' "
                "was not executed because "
                "human approval was rejected."
            ),
            "action_error": ("Human approval was rejected."),
            "action_execution_status": "blocked",
            "steps_executed": (
                state.get(
                    "steps_executed",
                    [],
                )
                + ["human_approval_rejected"]
            ),
        }

    # =====================================================
    # ROUTER AFTER HUMAN APPROVAL
    # =====================================================

    def route_after_human_approval(
        self,
        state: AgentState,
    ):

        approval_status = state.get(
            "approval_status",
            "rejected",
        )

        if approval_status == "approved":

            return "approved"

        return "rejected"

    # =====================================================
    # NODE 11
    # HANDLE APPROVAL DECISION
    # =====================================================

    def handle_approval_decision(
        self,
        state: AgentState,
    ):
        """
        Handle the result of human approval.

        Approved:
            Resume execution with ``execute_action``.

        Rejected:
            Skip ``execute_action`` and move to
            ``generate_response`` when available.

        Important:
            Approval is requested before ``prepare_next_step``
            in the direct approval path. Therefore ``next_step``
            is normally ``None`` when approval is granted. The
            approved action must explicitly resume at
            ``execute_action``.
        """

        approval_status = state.get(
            "approval_status",
            "rejected",
        )

        plan = state.get(
            "plan",
            [],
        )

        # -------------------------------------------------
        # Normalize plan
        # -------------------------------------------------

        normalized_plan = []

        for step in plan:

            if hasattr(
                step,
                "value",
            ):

                normalized_plan.append(step.value)

            else:

                normalized_plan.append(str(step))

        # =================================================
        # APPROVED
        # =================================================

        if approval_status == "approved":

            # Critical safety check: approval must only
            # resume a plan that actually contains the
            # action execution step.
            if "execute_action" not in normalized_plan:

                return {
                    "execution_status": "failed",
                    "stop_reason": (
                        "Approval was granted, but "
                        "execute_action is not present "
                        "in the execution plan."
                    ),
                    "error": (
                        "Approved action cannot continue "
                        "because execute_action is missing "
                        "from the plan."
                    ),
                }

            print("\n" + "=" * 80)
            print("APPROVAL GRANTED")
            print("=" * 80)

            print("Human approval received.")
            print("Resuming workflow with: execute_action")
            print(
                "The approved action will now be passed " "to the business-action tool."
            )

            # Approval happens before prepare_next_step in
            # the direct approval route. Do not depend on
            # state["next_step"] here. Explicitly restore
            # the action execution step.
            return {
                "current_step": "execute_action",
                "next_step": None,
                "execution_status": "running",
                "approval_status": "approved",
                "action_execution_status": "authorized",
                "retryable_failure": False,
                "stop_reason": "",
                "error": "",
            }

        # =================================================
        # REJECTED
        # =================================================

        response_step = None

        if "generate_response" in normalized_plan:

            response_step = "generate_response"

        if response_step:

            print("\n" + "=" * 80)
            print("APPROVAL REJECTED")
            print("=" * 80)

            print("Human approval was rejected.")
            print("Skipping execute_action.")
            print("Moving to generate_response.")

            return {
                "current_step": response_step,
                "next_step": None,
                "execution_status": "running",
                "approval_status": "rejected",
                "action_execution_status": "blocked",
                "retryable_failure": False,
                "stop_reason": "Human approval was rejected.",
            }

        # -------------------------------------------------
        # No response step available
        # -------------------------------------------------

        return {
            "execution_status": "completed",
            "stop_reason": "Action rejected by human.",
            "current_step": None,
            "next_step": None,
            "approval_status": "rejected",
            "action_execution_status": "blocked",
        }

    # =====================================================
    # NODE 12
    # SET NEXT STEP
    # =====================================================

    def set_next_step(
        self,
        state: AgentState,
    ):

        next_step = state.get("next_step")

        if next_step is None:

            return {"current_step": None}

        print(f"\nSetting Current Step : " f"{next_step}")

        return {"current_step": next_step}

    # =====================================================
    # BUILD LANGGRAPH
    # =====================================================

    def _build_graph(
        self,
    ):
        """
        Build and compile LangGraph.
        """

        builder = StateGraph(AgentState)

        # =================================================
        # NODES
        # =================================================

        builder.add_node(
            "classify_intent",
            self.classify_intent,
        )

        builder.add_node(
            "create_plan",
            self.create_plan,
        )

        builder.add_node(
            "initialize_execution",
            self.initialize_execution,
        )

        builder.add_node(
            "check_execution_limit",
            self.check_execution_limit,
        )

        builder.add_node(
            "supervisor_execute",
            self.supervisor_execute,
        )

        builder.add_node(
            "check_agent_result",
            self.check_agent_result,
        )

        builder.add_node(
            "prepare_next_step",
            self.prepare_next_step,
        )

        builder.add_node(
            "retry_execution",
            self.retry_execution,
        )

        builder.add_node(
            "request_user_information",
            self.request_user_information,
        )

        builder.add_node(
            "human_approval",
            self.human_approval,
        )

        builder.add_node(
            "handle_approval_decision",
            self.handle_approval_decision,
        )

        builder.add_node(
            "set_next_step",
            self.set_next_step,
        )

        # =================================================
        # START
        # =================================================

        builder.add_edge(
            START,
            "classify_intent",
        )

        # =================================================
        # INTENT → PLANNER
        #
        # IMPORTANT:
        # Do NOT use an unconditional edge here.
        #
        # If intent classification fails,
        # planning must not execute.
        # =================================================

        builder.add_conditional_edges(
            "classify_intent",
            self.route_after_intent_classification,
            {
                "continue": "create_plan",
                "stop": END,
            },
        )

        # =================================================
        # PLANNER → INITIALIZE
        # =================================================

        builder.add_edge(
            "create_plan",
            "initialize_execution",
        )

        # =================================================
        # INITIALIZE → EXECUTION CONTROL
        # =================================================

        builder.add_edge(
            "initialize_execution",
            "check_execution_limit",
        )

        # =================================================
        # EXECUTION CONTROL
        # =================================================

        builder.add_conditional_edges(
            "check_execution_limit",
            self.route_after_execution_limit,
            {
                "continue": "supervisor_execute",
                "stop": END,
            },
        )

        # =================================================
        # SUPERVISOR → RESULT CHECK
        # =================================================

        builder.add_edge(
            "supervisor_execute",
            "check_agent_result",
        )

        # =================================================
        # RESULT CHECK
        # =================================================

        builder.add_conditional_edges(
            "check_agent_result",
            self.route_after_agent_result,
            {
                "continue": "prepare_next_step",
                "retry": "retry_execution",
                "ask_user": "request_user_information",
                "human_approval": "human_approval",
                "stop": END,
            },
        )

        # =================================================
        # RETRY
        # =================================================

        builder.add_edge(
            "retry_execution",
            "check_execution_limit",
        )

        # =================================================
        # USER INFORMATION
        # =================================================

        builder.add_conditional_edges(
            "request_user_information",
            self.route_after_user_information,
            {
                "continue": "check_execution_limit",
                "stop": END,
            },
        )

        # =================================================
        # PREPARE NEXT STEP
        # =================================================

        builder.add_conditional_edges(
            "prepare_next_step",
            self.route_after_next_step,
            {
                "continue": "set_next_step",
                "human_approval": "human_approval",
                "stop": END,
            },
        )

        # =================================================
        # HUMAN APPROVAL
        # =================================================

        builder.add_edge(
            "human_approval",
            "handle_approval_decision",
        )

        # =================================================
        # APPROVAL DECISION
        # =================================================

        builder.add_conditional_edges(
            "handle_approval_decision",
            self.route_after_human_approval,
            {
                "approved": "check_execution_limit",
                "rejected": "check_execution_limit",
            },
        )

        # =================================================
        # NORMAL NEXT STEP
        # =================================================

        builder.add_edge(
            "set_next_step",
            "check_execution_limit",
        )

        # =================================================
        # CHECKPOINTER
        # =================================================

        checkpointer = MemorySaver()

        # =================================================
        # COMPILE
        # =================================================

        return builder.compile(checkpointer=checkpointer)

    # =====================================================
    # PUBLIC RUN METHOD
    # =====================================================

    def run(
        self,
        query: str,
    ):
        """
        Execute the workflow.

        Supports:

            - normal execution
            - human approval
            - user clarification
            - pause/resume
        """

        if not query or not query.strip():

            raise ValueError("Query cannot be empty.")

        # -------------------------------------------------
        # Unique workflow thread
        # -------------------------------------------------

        thread_id = f"agent-session-" f"{uuid4().hex}"

        config = {"configurable": {"thread_id": thread_id}}

        # -------------------------------------------------
        # Initial state
        # -------------------------------------------------

        initial_state: AgentState = {
            "query": query.strip(),
            "steps_executed": [],
            "execution_count": 0,
            "retry_count": 0,
            "execution_status": "running",
            "stop_reason": "",
            "approval_required": False,
            "approval_status": "not_required",
            "retryable_failure": False,
            "missing_information": "",
            "needs_user_input": False,
            "user_input_required": False,
            "confidence_clarification_completed": False,
        }

        # -------------------------------------------------
        # Start workflow
        # -------------------------------------------------

        result = self.graph.invoke(
            initial_state,
            config=config,
        )

        # -------------------------------------------------
        # Handle workflow interruptions
        # -------------------------------------------------

        while True:

            interrupts = result.get("__interrupt__")

            if not interrupts:

                return result

            print("\n" + "=" * 80)
            print("WORKFLOW PAUSED")
            print("=" * 80)

            # -------------------------------------------------
            # Extract interrupt payload
            # -------------------------------------------------

            interrupt_value = None

            try:

                interrupt_value = interrupts[0].value

            except (
                IndexError,
                AttributeError,
                TypeError,
            ):

                interrupt_value = interrupts[0]

            interrupt_type = "human_approval"

            if isinstance(
                interrupt_value,
                dict,
            ):

                interrupt_type = interrupt_value.get(
                    "type",
                    "human_approval",
                )

            # =================================================
            # USER INPUT
            # =================================================

            if interrupt_type == "user_input":

                print("Additional user " "information is required.")

                print("\nRequest:")

                print(interrupt_value)

                while True:

                    user_input = input("\nEnter required information: ").strip()

                    if user_input:

                        break

                    print("Please provide " "the required information.")

                print("\nResuming workflow...")

                result = self.graph.invoke(
                    Command(resume=user_input),
                    config=config,
                )

                continue

            # =================================================
            # HUMAN APPROVAL
            # =================================================

            print("Human approval is required " "before the workflow can continue.")

            print("\nApproval Request:")

            print(interrupt_value)

            print("\nOptions:")

            print("1. approve")

            print("2. reject")

            while True:

                decision = (
                    input("\nEnter decision " "(approve/reject): ").strip().lower()
                )

                if decision in {
                    "approve",
                    "approved",
                    "yes",
                    "y",
                }:

                    decision = "approved"

                    break

                if decision in {
                    "reject",
                    "rejected",
                    "no",
                    "n",
                }:

                    decision = "rejected"

                    break

                print("Invalid decision. " "Please enter " "'approve' or " "'reject'.")

            # -------------------------------------------------
            # Resume workflow
            # -------------------------------------------------

            print("\nResuming workflow...")

            result = self.graph.invoke(
                Command(resume=decision),
                config=config,
            )
