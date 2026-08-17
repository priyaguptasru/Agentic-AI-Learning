"""
Timeout Handling Test
=====================

Verifies that AgentWorkflow detects a slow Supervisor
execution as a timeout.

This test temporarily replaces Supervisor.execute()
only for this test.

No production code is modified.
"""

import time

from app6.workflows.agent_workflow import AgentWorkflow


def test_timeout_handling():

    print("\n" + "=" * 80)
    print("TEST: TIMEOUT HANDLING")
    print("=" * 80)

    workflow = AgentWorkflow()

    original_execute = workflow.supervisor.execute

    call_count = {
        "count": 0,
    }

    # -----------------------------------------------------
    # Simulate a slow Supervisor
    # -----------------------------------------------------

    def slow_supervisor(state):

        call_count["count"] += 1

        print("\n" + "-" * 80)
        print(f"SIMULATED SUPERVISOR EXECUTION " f"#{call_count['count']}")
        print("-" * 80)

        print("\nSimulating slow execution...")

        # Intentionally sleep longer than the
        # configured workflow timeout.
        time.sleep(workflow.AGENT_TIMEOUT_SECONDS + 5)

        return {
            "context": ("This response should not " "be reached before timeout."),
            "retryable_failure": False,
            "failure_type": "",
        }

    workflow.supervisor.execute = slow_supervisor

    try:

        # -------------------------------------------------
        # Initial state
        # -------------------------------------------------

        state = {
            "query": "What is routing?",
            "intent": "retrieval",
            "current_step": "retrieve_documents",
            "execution_status": "running",
            "retry_count": 0,
            "steps_executed": [],
            "retryable_failure": False,
            "failure_type": "",
            "agent_error": "",
        }

        print("\nInitial State:")
        print(state)

        print(f"\nConfigured timeout: " f"{workflow.AGENT_TIMEOUT_SECONDS} seconds")

        # =================================================
        # EXECUTE SUPERVISOR
        # =================================================

        print("\n" + "=" * 80)
        print("STARTING SLOW SUPERVISOR")
        print("=" * 80)

        result = workflow.supervisor_execute(state)

        print("\n" + "=" * 80)
        print("SUPERVISOR RESULT")
        print("=" * 80)

        print(result)

        # =================================================
        # VERIFY TIMEOUT
        # =================================================

        failure_type = result.get(
            "failure_type",
            "",
        )

        retryable = result.get(
            "retryable_failure",
            False,
        )

        agent_error = result.get(
            "agent_error",
            "",
        )

        print("\n" + "=" * 80)
        print("TIMEOUT VERIFICATION")
        print("=" * 80)

        print(f"Failure Type      : {failure_type}")

        print(f"Retryable Failure : {retryable}")

        print(f"Agent Error       : {agent_error}")

        # -------------------------------------------------
        # Expected timeout
        # -------------------------------------------------

        assert failure_type == "timeout", (
            "Expected failure_type='timeout', " f"but received: {failure_type}"
        )

        assert retryable is True, "Expected timeout to be " "retryable."

        print("\n✓ Timeout was detected.")

        print("✓ Timeout was classified as " "retryable.")

        print("\n" + "=" * 80)
        print("TIMEOUT TEST PASSED")
        print("=" * 80)

    finally:

        # -------------------------------------------------
        # Restore production Supervisor
        # -------------------------------------------------

        workflow.supervisor.execute = original_execute


if __name__ == "__main__":

    test_timeout_handling()
