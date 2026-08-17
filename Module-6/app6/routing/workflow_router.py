"""
Workflow Router
===============

Deterministic routing layer for Module-6.

Responsibilities
----------------

The LLM is responsible for:

    - Intent classification
    - Natural-language understanding
    - Plan generation

This router is responsible for deterministic decisions:

    - Workflow-step validation
    - Agent selection
    - Execution limits
    - Missing-information detection
    - Confidence checks
    - Retry decisions
    - Human-approval routing
    - Safe exits
    - Plan completion

The router must NOT make business decisions using an LLM.

This keeps workflow control predictable and production-friendly.
"""


class WorkflowRouter:
    """
    Deterministic workflow router.

    The router does not execute agents.

    It only decides what the workflow should do next.
    """

    # =====================================================
    # ROUTING DECISIONS
    # =====================================================

    CONTINUE = "continue"
    RETRY = "retry"
    ASK_USER = "ask_user"
    REQUIRE_APPROVAL = "require_approval"
    SAFE_EXIT = "safe_exit"
    COMPLETE = "complete"

    # =====================================================
    # CONFIGURATION
    # =====================================================

    DEFAULT_LOW_CONFIDENCE_THRESHOLD = 0.70

    DEFAULT_MAX_RETRIES = 2

    # =====================================================
    # ALLOWED WORKFLOW STEPS
    # =====================================================

    ALLOWED_STEPS = {
        "greeting",
        "retrieve_documents",
        "execute_sql",
        "validate_action",
        "execute_action",
        "generate_response",
    }

    # =====================================================
    # AGENT ROUTING
    # =====================================================

    AGENT_MAPPING = {
        "retrieve_documents": "retrieval_agent",
        "execute_sql": "sql_agent",
        "validate_action": "action_agent",
        "execute_action": "action_agent",
        "generate_response": "answer_agent",
    }

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        low_confidence_threshold: float = DEFAULT_LOW_CONFIDENCE_THRESHOLD,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        """
        Initialize deterministic routing configuration.

        Parameters
        ----------
        low_confidence_threshold:
            Confidence below this value can require
            additional user clarification.

        max_retries:
            Maximum number of retries for a retryable
            workflow failure.
        """

        if not 0.0 <= low_confidence_threshold <= 1.0:
            raise ValueError("low_confidence_threshold must be between 0.0 and 1.0.")

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

        self.low_confidence_threshold = low_confidence_threshold

        self.max_retries = max_retries

    # =====================================================
    # STEP VALIDATION
    # =====================================================

    def is_valid_step(
        self,
        step: str,
    ) -> bool:
        """
        Check whether a workflow step is supported.
        """

        if not isinstance(step, str):
            return False

        return step.strip() in self.ALLOWED_STEPS

    # =====================================================
    # AGENT SELECTION
    # =====================================================

    def get_agent_name(
        self,
        step: str,
    ):
        """
        Map a workflow step to its responsible agent.

        Greeting is handled directly by the workflow.
        """

        if step == "greeting":
            return None

        if step not in self.AGENT_MAPPING:
            raise ValueError(f"No agent is configured for workflow step: {step}")

        return self.AGENT_MAPPING[step]

    # =====================================================
    # EXECUTION LIMIT
    # =====================================================

    def execution_limit_reached(
        self,
        execution_count: int,
        max_execution_steps: int,
    ) -> bool:
        """
        Check whether the workflow has reached its
        maximum execution limit.
        """

        return execution_count >= max_execution_steps

    # =====================================================
    # STOP CONDITION
    # =====================================================

    def should_stop(
        self,
        state,
    ) -> bool:
        """
        Determine whether workflow execution should stop.
        """

        status = state.get(
            "execution_status",
            "running",
        )

        return status in {
            "failed",
            "stopped",
            "completed",
        }

    # =====================================================
    # PLAN COMPLETION
    # =====================================================

    def plan_completed(
        self,
        state,
    ) -> bool:
        """
        Determine whether all planned steps are complete.
        """

        next_step = state.get("next_step")

        return next_step is None

    # =====================================================
    # APPROVAL REQUIRED
    # =====================================================

    def approval_required(
        self,
        state,
    ) -> bool:
        """
        Determine whether human approval is required.
        """

        return bool(
            state.get(
                "approval_required",
                False,
            )
        )

    # =====================================================
    # APPROVAL PENDING
    # =====================================================

    def approval_pending(
        self,
        state,
    ) -> bool:
        """
        Determine whether approval is currently waiting
        for a human decision.
        """

        return (
            self.approval_required(state)
            and state.get(
                "approval_status",
                "",
            )
            == "pending"
        )

    # =====================================================
    # ACTION EXECUTION SAFETY
    # =====================================================

    def can_execute_action(
        self,
        state,
    ) -> bool:
        """
        Determine whether an action may execute.

        Approval is a deterministic safety gate.
        """

        if self.approval_required(state):
            return (
                state.get(
                    "approval_status",
                    "",
                )
                == "approved"
            )

        return True

    # =====================================================
    # MISSING INFORMATION
    # =====================================================

    def missing_information(
        self,
        state,
    ) -> bool:
        """
        Determine whether the workflow needs additional
        information from the user.

        Agents can communicate this through:

            missing_information
            needs_user_input
            user_input_required
        """

        if state.get("needs_user_input") is True:
            return True

        if state.get("user_input_required") is True:
            return True

        missing = state.get("missing_information")

        if isinstance(
            missing,
            str,
        ):
            return bool(missing.strip())

        if isinstance(
            missing,
            (list, tuple, set),
        ):
            return len(missing) > 0

        return bool(missing)

    # =====================================================
    # LOW CONFIDENCE
    # =====================================================

    def low_confidence(
        self,
        state,
    ) -> bool:
        """
        Determine whether the workflow confidence is
        below the configured threshold.

        This is intentionally deterministic.
        """

        confidence = state.get("confidence")

        if confidence is None:
            return False

        try:
            confidence = float(confidence)
        except (
            TypeError,
            ValueError,
        ):
            return False

        return confidence < self.low_confidence_threshold

    # =====================================================
    # RETRY COUNT
    # =====================================================

    def retry_count(
        self,
        state,
    ) -> int:
        """
        Return the current retry count.
        """

        value = state.get(
            "retry_count",
            0,
        )

        try:
            return max(
                0,
                int(value),
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0

    # =====================================================
    # RETRY AVAILABLE
    # =====================================================

    def retry_available(
        self,
        state,
    ) -> bool:
        """
        Determine whether another retry is allowed.
        """

        return self.retry_count(state) < self.max_retries

    # =====================================================
    # RETRYABLE FAILURE
    # =====================================================

    def retryable_failure(
        self,
        state,
    ) -> bool:
        """
        Determine whether the current failure is marked
        as retryable.

        The workflow should explicitly mark retryable
        failures rather than retrying every possible error.
        """

        return bool(
            state.get(
                "retryable_failure",
                False,
            )
        )

    # =====================================================
    # MAIN ROUTING DECISION
    # =====================================================

    def route(
        self,
        state,
    ) -> str:
        """
        Determine the next deterministic workflow decision.

        Priority:

        1. Terminal states
        2. Missing information
        3. Pending human approval
        4. Retryable failures
        5. Low confidence
        6. Continue execution
        """

        status = state.get(
            "execution_status",
            "running",
        )

        # -------------------------------------------------
        # Terminal states
        # -------------------------------------------------

        if status == "completed":
            return self.COMPLETE

        if status in {
            "failed",
            "stopped",
        }:
            return self.SAFE_EXIT

        # -------------------------------------------------
        # Missing information
        # -------------------------------------------------

        if self.missing_information(state):
            return self.ASK_USER

        # -------------------------------------------------
        # Human approval
        # -------------------------------------------------

        if self.approval_pending(state):
            return self.REQUIRE_APPROVAL

        # -------------------------------------------------
        # Retryable failure
        # -------------------------------------------------

        if self.retryable_failure(state):

            if self.retry_available(state):
                return self.RETRY

            return self.SAFE_EXIT

        # -------------------------------------------------
        # Low confidence
        # -------------------------------------------------

        if self.low_confidence(state):

            # Do not repeatedly interrupt after a user
            # has already supplied clarification.
            if not state.get(
                "confidence_clarification_completed",
                False,
            ):
                return self.ASK_USER

        # -------------------------------------------------
        # Continue
        # -------------------------------------------------

        return self.CONTINUE
