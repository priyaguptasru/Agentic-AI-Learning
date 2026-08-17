"""
Full Retry Integration Test
===========================

Verifies:

Supervisor execution
        ↓
failure
        ↓
check_agent_result
        ↓
WorkflowRouter
        ↓
retry_execution
        ↓
Supervisor execution again
        ↓
success

The Supervisor is temporarily patched only for this test.
No production files are modified.
"""

from app6.workflows.agent_workflow import AgentWorkflow


def test_retry_integration():

    print("\n" + "=" * 80)
    print("TEST: FULL RETRY INTEGRATION")
    print("=" * 80)

    workflow = AgentWorkflow()

    original_execute = workflow.supervisor.execute

    call_count = {
        "count": 0,
    }

    # -----------------------------------------------------
    # Temporary Supervisor behavior
    # -----------------------------------------------------

    def simulated_supervisor(state):

        call_count["count"] += 1

        attempt = call_count["count"]

        print("\n" + "-" * 80)
        print(f"SIMULATED SUPERVISOR EXECUTION #{attempt}")
        print("-" * 80)

        # First execution deliberately fails.
        if attempt == 1:

            print("Simulating transient retrieval failure...")

            return {
                "agent_error": ("Simulated transient " "retrieval failure."),
                "error": ("Simulated transient " "retrieval failure."),
                "retryable_failure": True,
                "failure_type": "execution_error",
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["retrieve_documents_failed"]
                ),
            }

        # Second execution succeeds.
        print("Simulated retrieval succeeded.")

        return {
            "context": ("Simulated retrieved context " "after retry."),
            "steps_executed": (
                state.get(
                    "steps_executed",
                    [],
                )
                + ["retrieve_documents"]
            ),
            "retryable_failure": False,
            "failure_type": "",
            "agent_error": "",
        }

    workflow.supervisor.execute = simulated_supervisor

    try:

        # -------------------------------------------------
        # Build state that starts at retrieval
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

        # =================================================
        # EXECUTION #1
        # =================================================

        print("\n" + "=" * 80)
        print("EXECUTION #1")
        print("=" * 80)

        first_result = workflow.supervisor_execute(state)

        print("\nFirst Execution Result:")
        print(first_result)

        # Merge state exactly as workflow would.
        state.update(first_result)

        # -------------------------------------------------
        # Verify failure
        # -------------------------------------------------

        assert state.get("retryable_failure") is True

        print("\n✓ First execution failed " "as a retryable failure.")

        # =================================================
        # CHECK RETRY ROUTING
        # =================================================

        print("\n" + "=" * 80)
        print("CHECK RETRY ROUTING")
        print("=" * 80)

        decision = workflow.workflow_router.route(state)

        print(f"\nRouter Decision : {decision}")

        assert decision == "retry"

        print("✓ WorkflowRouter correctly " "selected RETRY.")

        # =================================================
        # RETRY
        # =================================================

        print("\n" + "=" * 80)
        print("EXECUTING RETRY")
        print("=" * 80)

        retry_result = workflow.retry_execution(state)

        print("\nRetry Result:")
        print(retry_result)

        state.update(retry_result)

        assert state.get("retry_count") == 1

        print("\n✓ Retry count incremented " "to 1.")

        # =================================================
        # EXECUTION #2
        # =================================================

        print("\n" + "=" * 80)
        print("EXECUTION #2")
        print("=" * 80)

        second_result = workflow.supervisor_execute(state)

        print("\nSecond Execution Result:")
        print(second_result)

        state.update(second_result)

        # -------------------------------------------------
        # Verify success
        # -------------------------------------------------

        assert (
            state.get(
                "retryable_failure",
                False,
            )
            is False
        )

        assert (
            state.get(
                "context",
                "",
            )
            == "Simulated retrieved context after retry."
        )

        print("\n✓ Second execution succeeded.")

        # =================================================
        # FINAL VERIFICATION
        # =================================================

        print("\n" + "=" * 80)
        print("FINAL VERIFICATION")
        print("=" * 80)

        print(f"Supervisor executions : " f"{call_count['count']}")

        print(f"Retry count          : " f"{state.get('retry_count')}")

        print(f"Final failure status  : " f"{state.get('retryable_failure')}")

        assert call_count["count"] == 2

        assert state["retry_count"] == 1

        assert state["retryable_failure"] is False

        print("\n" + "=" * 80)
        print("FULL RETRY INTEGRATION TEST PASSED")
        print("=" * 80)

        print(
            "\nVerified flow:"
            "\n"
            "Supervisor failure"
            "\n    ↓"
            "\nWorkflowRouter → RETRY"
            "\n    ↓"
            "\nretry_execution"
            "\n    ↓"
            "\nSupervisor execution again"
            "\n    ↓"
            "\nSUCCESS"
        )

    finally:

        # -------------------------------------------------
        # Always restore production Supervisor
        # -------------------------------------------------

        workflow.supervisor.execute = original_execute


if __name__ == "__main__":

    test_retry_integration()
