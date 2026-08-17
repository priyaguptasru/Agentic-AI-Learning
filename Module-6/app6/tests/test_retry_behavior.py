"""
Retry Logic Test
================

Tests the deterministic retry mechanism of Module-6.

This test does NOT call the LLM, database, retrieval system,
or external business systems.

It directly verifies:

1. Retryable failure detection
2. Retry routing
3. Retry count
4. Maximum retry limit
5. Safe exit after retry exhaustion
"""

from app6.workflows.agent_workflow import AgentWorkflow


def test_retry_logic():

    print("\n" + "=" * 80)
    print("TEST: RETRY LOGIC")
    print("=" * 80)

    workflow = AgentWorkflow()

    # -----------------------------------------------------
    # Simulated retryable failure
    # -----------------------------------------------------

    state = {
        "current_step": "retrieve_documents",
        "execution_status": "running",
        "retry_count": 0,
        "retryable_failure": True,
        "failure_type": "execution_error",
        "error": "Simulated retrieval failure",
    }

    print("\nInitial State:")
    print(state)

    # =====================================================
    # ATTEMPT 1
    # =====================================================

    print("\n" + "-" * 80)
    print("ATTEMPT 1")
    print("-" * 80)

    decision = workflow.workflow_router.route(state)

    print(f"Router Decision : {decision}")

    assert decision == "retry"

    # -----------------------------------------------------
    # Execute retry
    # -----------------------------------------------------

    retry_result = workflow.retry_execution(state)

    print("\nRetry Result:")
    print(retry_result)

    assert retry_result["retry_count"] == 1

    # Update state
    state.update(retry_result)

    # Simulate another failure
    state.update(
        {
            "execution_status": "running",
            "retryable_failure": True,
            "failure_type": "execution_error",
            "error": "Simulated retrieval failure - attempt 2",
        }
    )

    # =====================================================
    # ATTEMPT 2
    # =====================================================

    print("\n" + "-" * 80)
    print("ATTEMPT 2")
    print("-" * 80)

    decision = workflow.workflow_router.route(state)

    print(f"Router Decision : {decision}")

    assert decision == "retry"

    retry_result = workflow.retry_execution(state)

    print("\nRetry Result:")
    print(retry_result)

    assert retry_result["retry_count"] == 2

    state.update(retry_result)

    # Simulate another failure
    state.update(
        {
            "execution_status": "running",
            "retryable_failure": True,
            "failure_type": "execution_error",
            "error": "Simulated retrieval failure - attempt 3",
        }
    )

    # =====================================================
    # ATTEMPT 3
    # =====================================================

    print("\n" + "-" * 80)
    print("ATTEMPT 3")
    print("-" * 80)

    decision = workflow.workflow_router.route(state)

    print(f"Router Decision : {decision}")

    # MAX_RETRIES = 2
    #
    # retry_count is already 2.
    #
    # Therefore another retry must NOT be allowed.

    assert decision == "safe_exit"

    # -----------------------------------------------------
    # Verify retry availability
    # -----------------------------------------------------

    retry_available = workflow.workflow_router.retry_available(state)

    print(f"Retry Available : {retry_available}")

    assert retry_available is False

    print("\n" + "=" * 80)
    print("RETRY TEST PASSED")
    print("=" * 80)

    print(
        "\nExpected behavior:"
        "\nAttempt 1 -> RETRY"
        "\nAttempt 2 -> RETRY"
        "\nAttempt 3 -> SAFE_EXIT"
    )


if __name__ == "__main__":

    test_retry_logic()
